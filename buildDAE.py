import sys, struct, numpy
from collada import *

def createDAE(mesh, mat, DAE, counters):
	for i in range(len(DAE)):
		materialName = "material" + str(counters[i])
		mesh.geometries.append(DAE[i])

		matnode = scene.MaterialNode(materialName, mat[i], inputs=[])
		geomnode = scene.GeometryNode(DAE[i], [matnode])
		node = scene.Node("node" + str(i), children=[geomnode])

		myscene = scene.Scene("myscene", [node])
		mesh.scenes.append(myscene)
	mesh.scene = myscene

	mesh.write(sys.argv[1].rsplit("\\", 2)[-1].replace(".gmx", "") + '.dae')

def createGEOM(mesh, model, counter):
	#vert_floats = [-50,50,50,50,50,50,-50,-50,50,50,-50,50,-50,50,-50,50,50,-50,-50,-50,-50,50,-50,-50]
	#normal_floats = [0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,0,-1,0,0,-1,0,0,-1,0,0,-1,0,-1,0,0,-1,0,0,-1,0,0,-1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,-1,0,0,-1,0,0,-1,0,0,-1]
	vert_src = source.FloatSource("verts-array", numpy.array(model[3]), ('X', 'Y', 'Z'))
	normal_src = source.FloatSource("normals-array", numpy.array(model[4]), ('X', 'Y', 'Z'))
	uv_src = source.FloatSource("uv-array", numpy.array(model[5]), ('S', 'T'))

	geom = geometry.Geometry(mesh, "geometry" + str(counter), "mycube", [vert_src, normal_src, uv_src])

	input_list = source.InputList()
	input_list.addInput(0, 'VERTEX', "#verts-array")
	#input_list.addInput(1, 'NORMAL', "#normals-array")
	input_list.addInput(1, 'TEXCOORD', "#uv-array", set="0")

	#indices = numpy.array([0,0,2,1,3,2,0,0,3,2,1,3,0,4,1,5,5,6,0,4,5,6,4,7,6,8,7,9,3,10,6,8,3,10,2,11,0,12,4,13,6,14,0,12,6,14,2,15,3,16,7,17,5,18,3,16,5,18,1,19,5,20,7,21,6,22,5,20,6,22,4,23])
	numpy_indices = numpy.array(model[6])
	
	'''vcounts = []
	for o in range(int(model[2] / 3)):
		vcounts.append(3)
	numpy_vcounts = numpy.array(vcounts)'''
	
	triset = geom.createTriangleSet(numpy_indices, input_list, "material" + str(counter))
	geom.primitives.append(triset)
	
	return geom

def PADX(size):
	f.seek(f.tell() + size - 8)

def MESH(size):
	unk0 =			struct.unpack(">i",f.read(4))[0]
	vertSize =		struct.unpack(">H",f.read(2))[0]
	vertCount =		struct.unpack(">H",f.read(2))[0]
	unk1 =			struct.unpack(">i",f.read(4))[0]
	indexCount =	struct.unpack(">i",f.read(4))[0]
	unk2 =			struct.unpack(">i",f.read(4))[0]
	unk3 =			struct.unpack(">i",f.read(4))[0]
	unk4 =			struct.unpack(">i",f.read(4))[0]
	unk5 =			struct.unpack(">i",f.read(4))[0]
	f.seek(f.tell() - 40 + size)
	return [vertSize, vertCount, indexCount]

def VERT(size, vertSize, vertCount):
	start = int(f.tell())
	vert_floats = []
	normal_floats = []
	uv_floats = []
	i = 0
	for i in range(vertCount):
		if(vertSize == 36):
			unk8 = struct.unpack(">i",f.read(4))[0]
		
		verts = struct.unpack(">3f",f.read(12))
		
		if(vertSize > 20):
			normals = struct.unpack(">3f",f.read(12))
		else:
			normals = {0.0, 0.0, 0.0}
		
		uvs = struct.unpack(">2f",f.read(8))
		
		for j in range(3):
			vert_floats.append(verts[j])
			normal_floats.append(normals[j])
		for h in range(2):
			uv_floats.append(uvs[h])
	f.seek(start - 8 + size)
	return [vert_floats, normal_floats, uv_floats]

def INDX(size, indexCount):
	start = int(f.tell())
	indices = []
	i = 0
	for i in range(int(indexCount / 3)):
		index = struct.unpack(">3H", f.read(6))
		
		for j in range(3):
			indices.append(index[2 - j])
			indices.append(index[2 - j])
	f.seek(start - 8 + size)
	return(indices)

def VMAP(size):
	print("VMAPs were not figured out yet.")
	f.seek(f.tell() - 8 + size)

def readGMX():
	f.seek(struct.unpack(">i",f.read(4))[0])
	section = str(struct.unpack(">4s",f.read(4))[0]).replace("b", "", 1).replace("'", "")
	mesh = []
	meshID = 0
	inside_mesh = False
	while(section != "ENDX"):
		print(section)
		size = struct.unpack(">i",f.read(4))[0]
		if(section == "PADX"):
			PADX(size)
		elif(section == "MESH"):
			meshID = meshID + 1
			inside_mesh = True
			mesh.append(MESH(size))
		elif(inside_mesh):
			if(section == "VERT"):
				verts = VERT(size, mesh[meshID - 1][0], mesh[meshID - 1][1])
				mesh[meshID - 1].append(verts[0])
				mesh[meshID - 1].append(verts[1])
				mesh[meshID - 1].append(verts[2])
			elif(section == "INDX"):
				mesh[meshID - 1].append(INDX(size, mesh[meshID - 1][2]))
			elif(section == "VMAP"):
				VMAP(size)
		
		section = str(struct.unpack(">4s",f.read(4))[0]).replace("b", "", 1).replace("'", "")
	return mesh

def main():
	mesh = Collada()
	
	axis = asset.UP_AXIS.Z_UP
	mesh.assetInfo.upaxis = axis
	'''
	effect = material.Effect("effect0", [], "phong", diffuse=(1,0,0), specular=(0,1,0))
	mat = material.Material("material0", "mymaterial", effect)
	mesh.effects.append(effect)
	mesh.materials.append(mat)
	'''
	model = readGMX()
	DAE = []
	mat = []
	counters = []
	for i in range(len(model)):
		counter = i
		if(model[i][1] != 0 and model[i][2] != 0):
			materialName = "material" + str(counter)
			image = material.CImage(materialName + "-image", sys.argv[1].rsplit("\\", 2)[-1].replace(".gmx", "") + '.png')
			surface = material.Surface(materialName + "-image-surface", image)
			sampler2d = material.Sampler2D(materialName + "-image-sampler", surface)
			map1 = material.Map(sampler2d, "UVSET0")
			
			effect = material.Effect(materialName + "-effect", [surface, sampler2d], "lambert",\
							emission=(0.0, 0.0, 0.0, 1), ambient=(0.0, 0.0, 0.0, 1),  diffuse=map1,\
							transparent=map1, transparency=0.0, double_sided=True)
			
			mat.append(material.Material(materialName + "ID", materialName, effect))
			
			mesh.effects.append(effect)
			mesh.materials.append(mat[i])
			DAE.append(createGEOM(mesh, model[i], counter))
			
			counters.append(counter)
	createDAE(mesh, mat, DAE, counters)

if __name__ == "__main__":
	print("")
	print("")
	print("Build GMX Program by Mystixor")
	print("")
	if len(sys.argv) < 2:
		print('Insufficient arguments. Please supply a GMX file.')
		exit()
	if len(sys.argv) > 2:
		print('Insufficient arguments. Please supply only one GMX file.')
		exit()
	else:
		f = open(sys.argv[1], 'rb')
		word = str(struct.unpack(">4s",f.read(4))[0]).replace("b", "", 1).replace("'", "")
		if word != "GMX2":
			print("Error 2: Unusual Filetype detected")
			print("File Name: {}".format(sys.argv[1].rsplit("\\", 2)[-1]))
			print('File is the wrong format. Please inform me of this, if you think the format should be supported. Format Given : ' + str(word))
			exit()
	print("File accepted!")
	
	main()