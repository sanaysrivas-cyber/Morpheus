"""Read-only transform extraction for the 26MBB-000 Inventor AP214 export.

Usage: python3 tools/audit_step.py /path/to/26MBB-000.stp > audit.json
This is a scoped extractor for this export, not a general STEP geometry kernel.
All placements are normalized to millimetres before composing transforms.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def refs(text):
    return [int(v) for v in re.findall(r'#(\d+)', text)]


def numbers(text):
    return [float(v) for v in text[text.rfind('(') + 1:].rstrip(')').split(',')]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def unit(v):
    length = math.sqrt(dot(v, v))
    return [x/length for x in v]


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def inverse_rigid(a):
    rotation = [[a[j][i] for j in range(3)] for i in range(3)]
    return [rotation[i] + [-sum(rotation[i][j]*a[j][3] for j in range(3))]
            for i in range(3)] + [[0, 0, 0, 1]]


def point(matrix, vector):
    return [sum(matrix[i][j]*vector[j] for j in range(3))+matrix[i][3] for i in range(3)]


def vector(matrix, v):
    return [sum(matrix[i][j]*v[j] for j in range(3)) for i in range(3)]


def extract(path):
    raw = path.read_bytes()
    source = raw.decode()
    entities = {int(m[1]): m[2].replace('\n', '').replace('\r', '')
                for m in re.finditer(r'#(\d+)\s*=\s*(.*?);', source, re.S)}

    def scale(representation):
        context = entities[refs(entities[representation])[-1]]
        units = refs(re.search(r'GLOBAL_UNIT_ASSIGNED_CONTEXT\(\((.*?)\)\)', context)[1])
        length_unit = entities[units[0]]
        if "'inch'" in length_unit:
            return 25.4
        if 'SI_UNIT(.MILLI.,.METRE.)' in length_unit:
            return 1.0
        raise ValueError('Unsupported length unit: ' + length_unit)

    def placement(entity, factor):
        origin_id, z_id, x_id = refs(entities[entity])
        origin = [n*factor for n in numbers(entities[origin_id])]
        z_axis, x_axis = unit(numbers(entities[z_id])), unit(numbers(entities[x_id]))
        assert abs(dot(z_axis, x_axis)) < 1e-8, 'Nonorthogonal placement'
        y_axis = cross(z_axis, x_axis)
        return [[x_axis[i], y_axis[i], z_axis[i], origin[i]] for i in range(3)] + [[0, 0, 0, 1]]

    children, transforms = {}, {}
    for entity, value in entities.items():
        if value.startswith('NEXT_ASSEMBLY_USAGE_OCCURRENCE('):
            parent, child = refs(value)
            children.setdefault(parent, []).append((entity, child))
        if value.startswith('CONTEXT_DEPENDENT_SHAPE_REPRESENTATION('):
            relationship, definition = refs(value)
            occurrence = refs(entities[definition])[-1]
            child_rep, parent_rep, transform = refs(entities[relationship])
            child_frame, parent_frame = refs(entities[transform])
            matrix = multiply(placement(parent_frame, scale(parent_rep)),
                              inverse_rigid(placement(child_frame, scale(child_rep))))
            transforms[occurrence] = dict(matrix_mm=matrix, transform=transform,
                                          child_frame=child_frame, parent_frame=parent_frame)

    # Geometry evidence: motor cylinders are parallel to local Y; axle cylinders to Z.
    for surface in [485317, 485325, 485329, 485334]:
        axis = refs(entities[surface])[0]
        direction = numbers(entities[refs(entities[axis])[1]])
        assert abs(abs(direction[1])-1) < 1e-8
    for surface in [484540, 485180]:
        axis = refs(entities[surface])[0]
        direction = numbers(entities[refs(entities[axis])[1]])
        assert abs(abs(direction[2])-1) < 1e-8

    rows = []
    drivetrain = 1573578
    for occurrence, product in children[drivetrain]:
        name = entities[product]
        if not any(s in name for s in ['Mecanum-Wheel', '435RPM', 'REX Shaft',
                                       'Steel Milter Gear', 'REV-Control-Hub',
                                       'REV-Expansion-Hub', 'Intake Ramp']):
            continue
        row = dict(occurrence=occurrence, product_definition=product,
                   definition=name, **transforms[occurrence])
        matrix = row['matrix_mm']
        if 'Mecanum-Wheel' in name:
            axles = []
            for roller_occ, roller_pd in children[product]:
                if 'roller assembly' not in entities[roller_pd]:
                    continue
                for axle_occ, axle_pd in children[roller_pd]:
                    if 'roller axle' not in entities[axle_pd]:
                        continue
                    composed = multiply(multiply(matrix, transforms[roller_occ]['matrix_mm']),
                                        transforms[axle_occ]['matrix_mm'])
                    axles.append(dict(path=[occurrence, roller_occ, axle_occ],
                                      midpoint_mm=point(composed, [0, 0, 22.75]),
                                      axis=unit(vector(composed, [0, 0, 1]))))
            assert len(axles) == 10
            center = [sum(a['midpoint_mm'][i] for a in axles)/len(axles) for i in range(3)]
            helicity = []
            for axle in axles:
                radial = [0, axle['midpoint_mm'][1]-center[1], axle['midpoint_mm'][2]-center[2]]
                tangent = unit(cross([1, 0, 0], radial))
                helicity.append(dot(axle['axis'], [1, 0, 0])*dot(axle['axis'], tangent))
            assert all(abs(abs(h)-0.5) < 1e-6 for h in helicity), helicity
            row.update(roller_center_mm=center, roller_axles=axles,
                       top_roller_axis_parallel_to=[1, 0, 1 if helicity[0] > 0 else -1])
        if '435RPM' in name:
            row['motor_local_positive_y_axis'] = unit(vector(matrix, [0, 1, 0]))
        rows.append(row)
    assert sum('Mecanum-Wheel' in r['definition'] for r in rows) == 4
    assert sum('435RPM' in r['definition'] for r in rows) == 4
    return dict(source=path.name, sha256=hashlib.sha256(raw).hexdigest(),
                byte_count=len(raw), coordinate_frame='drivetrain #1573578; mm; +Y up; +Z proposed front; +X left',
                method='T_parent_child = placement_parent_mm * inverse(placement_child_mm)',
                geometry_evidence=dict(motor_cylinders=[485317, 485325, 485329, 485334],
                                       roller_axle_cylinders=[484540, 485180]), occurrences=rows)


if __name__ == '__main__':
    print(json.dumps(extract(Path(sys.argv[1])), indent=2))
