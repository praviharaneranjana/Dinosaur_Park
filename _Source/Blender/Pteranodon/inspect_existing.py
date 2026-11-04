import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out={}
for p in root.glob('*.blend'):
    with bpy.data.libraries.load(str(p),link=False) as (src,dst):
        out[p.name]={'objects':list(src.objects)[:25], 'scenes':list(src.scenes)}
print('EXISTING_BLEND_INVENTORY',json.dumps(out))
