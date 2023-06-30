import bpy
from mathutils import Vector

L=[]

# Boucler à travers tous les objets dans la scène
for obj in bpy.context.scene.objects:
    # Sélectionner l'objet
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    # Mettre à jour la vue 3D
    if len(obj.name) == 9:
        bpy.context.view_layer.objects.active = obj
        num = int(obj.name[-3:])
        if num %10 == 0 :
            print(num)  # pour connaître l'avancement du programme
        T = []
        for frame in range(1, 3712):
            bpy.context.scene.frame_current = frame
            bbox = obj.bound_box
            center = sum((Vector(b) for b in bbox), Vector()) / 8

            # Placer le 3D curseur au centre géométrique de l'objet
            bpy.context.scene.cursor.location = obj.matrix_world @ center
            T.append(bpy.context.scene.cursor.location[:3])
        L.append(T)

with open("C:/Users/pubti/Documents/mp/location.txt", "w") as f :
    for i in range(len(L[0])):
        if i%100 == 0:
            print(f"{i}/ {len(L[0])}")
        line = ""
        for j in range(len(L)):
            line += str(L[j][i]) + ";"
        line = line[:-1] + "\n"
        f.write(line)