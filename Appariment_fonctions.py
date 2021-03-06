###
# Auteur : Amine MEDAD (UPPA)
# Projet : Choucas
# Contact: medadamine@gmail.com
###




import fiona
from shapely.geometry import shape


import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER



###
# Transformer le systemes de coordonées d'une trace GPS (format GPX) en Lamber_93 EPSG:2154
###

def gpx_transform_crs(fname, crs_origin, crs_final):
	import geopandas as gpd
	import fiona

	#layer_gpx = fiona.open(fname, layer='tracks')
	layer_gpx_track_points = fiona.open(fname, layer = 'track_points')


	if crs_origin=='4326' and crs_final == '2154':
		
		gdf = gpd.GeoDataFrame.from_features([feature for feature in layer_gpx_track_points], crs={'init': 'epsg:4326'})
		gdf_track_points_lamber = gdf.to_crs({'init': 'epsg:2154'})

		print(gdf_track_points_lamber)

	output_fname_lamber93 = fname[0:int(len(fname))-4]+"TRACE_lamber_93.GeoJSON"
	gdf_track_points_lamber.to_file(output_fname_lamber93, driver='GeoJSON')
	return gdf_track_points_lamber


###
# Transformer le systemes de coordonées d'un Geojson en Lamber_93 EPSG:2154
###
def lecture_geojson_dataframe_transform_crs_multipolygone_OSM(fname, crs_forme_final):
	import geopandas as gpd
	import fiona
	from fiona.crs import from_epsg

	df = gpd.read_file(fname)


	if (crs_forme_final == '2154'):

		df = df.to_crs({'init': 'epsg:2154'})

	if (crs_forme_final) == '4326':

		df = df.to_crs({'init': 'epsg:4326'})

	output_fname_lamber93 = fname[0:int(len(fname))-8]+"_lamber_93.GeoJSON"
	df.to_file(output_fname_lamber93, driver='GeoJSON')

	
	#df est une geodataframe sous forme d'un dictionaire avec des clés (Keys) et  l'ensemble des colonnes issues du geojson: geometry (Lamber93, title, findname...
	return df, output_fname_lamber93

def lecture_geojson_dataframe_transform_crs(fname, crs_forme_final):
	import geopandas as gpd

	df = gpd.read_file(fname)
	if (crs_forme_final == '2154'):

		df = df.to_crs({'init': 'epsg:2154'})

	if (crs_forme_final) == '4326':

		df = df.to_crs({'init': 'epsg:4326'})

	output_fname_lamber93 = fname[0:int(len(fname))-8]+"_lamber_93.GeoJSON"
	df.to_file(output_fname_lamber93, driver='GeoJSON')

	
	#df est une geodataframe sous forme d'un dictionaire avec des clés (Keys) et  l'ensemble des colonnes issues du geojson: geometry (Lamber93, title, findname...
	return df, output_fname_lamber93


def lecture_gpx(trace_file):

	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint
	import fiona
	from shapely.geometry import shape

	#fiona.listlayers(trace_file)
	layer = fiona.open(trace_file, layer='tracks')

	geom = layer[0]
	#print(geom['geometry']['coordinates'])
	data = {'type': 'MultiLineString', 'coordinates': geom['geometry']['coordinates']}
	#print(data)
	shp = shape(data)

	#shp_buffer = shp.buffer(10.0)
	#print(shp_buffer)

	#with fiona.open(trace_file+"_buffer_10_.shp", 'w') as dst:
	#	dst.write(shp_buffer)

	trace_multipoint = MultiPoint(geom['geometry']['coordinates'][0])
	#print(trace_multipoint)
	return shp, layer,trace_multipoint, geom['geometry']['coordinates'][0]
    #shp_buffer.write(trace_file+"_buffer_10_.shp")


def JSON_TO_GEOJSON(in_Json_file, out_Geogson_file):
	from sys import argv
	from os.path import exists
	import simplejson as json 

	#script, in_Json_file, out_Geogson_file = argv

	data = json.load(open(in_Json_file))
	# for d in data:
	#     print(d)
#ATTENTION LA LATITUDE ET LA LONGITUDE SONT INVERSER DANS LE FICHER ISSUS DE PERDIDO DONC LORS DE LA CONSTRUCTION DU GEOJSON 
#J'AI INVERSER L'ORDRE DANS : "coordinates": [float (d["lat"]), float(d["lng"])], L'ORDRE EXACTE ETANT : "coordinates": [float (d["lng"]), float(d["lat"])],
	geojson = {
	    "type": "FeatureCollection",
	    "features": [
	    {
	        "type": "Feature",
	        "geometry" : {
	            "type": "Point",
	            "coordinates": [float (d["lat"]), float(d["lng"])],
	            },
	        "properties" : d,
	     } for d in data]
	}


	output = open(out_Geogson_file, 'w')
	json.dump(geojson, output)





#buffer_size en degrée si crs = 4326

###
# établir un buffer autour des objets spatiaux (ex: trace GPS : point) d'une geodataframe (gdf) en entrée
###

def buffer_fixe_shape_GPX_lamber(gdf, buffer_size, gpx_fname):
	
	
	import geopandas as gpd

	liste_points = []
	
	for index, row in gdf.iterrows():
		#print(index, row)
		p = row.geometry

		p_buffer = p.buffer(buffer_size)
		

		liste_points.append(p_buffer)

	#shp_buffer = shp.buffer(buffer_size)
	#return shp_buffer
	gdf.geometry = liste_points
	out_gpx_buffer_file = gpx_fname[0:len(gpx_fname)-4]+"_trace_avec_Buffer_"+str(buffer_size)+"m.geojson"
	
	gdf.to_file(out_gpx_buffer_file, driver='GeoJSON')

	return liste_points










def construction_bufffer_fixe(gpx, buffer_rayon_degree, SEGMENTS, DISSOLVE, output_file):
	import processing
	
	return (processing.runandload("qgis:fixeddistancebuffer", gpx, buffer_rayon_degree, SEGMENTS, DISSOLVE, output_file))

#Lire les fichier de type geojson 
def lecture_geojson(fname, type_objets):
	import geopandas as gpd
	import fiona
	from shapely.geometry import shape
	from shapely.geometry import Point, MultiPoint

	layer = fiona.open(fname)

	df = gpd.read_file(fname)

	ENE_points=[]

	if type_objets =='ponctuel':
		for e in layer:
			p = e['geometry']
			#point = Point(p['coordinates'])
			point = p['coordinates']
			ENE_points.append(point)

		layer_multipoint2 = MultiPoint([])
		return  layer, layer_multipoint2,  df

	
	else:
		return layer, df



def zone_etude_choucas(file_name):
	import geopandas as gpd

	zone_choucas = gpd.read_file(file_name)
	return zone_choucas


###
# Filtration des ENE (tout type) géolocalisées hors contexte (zone choucas). Utilisé pour la phase de  l'intersection entres la trace GPS et les ENE geocodées dans le texte (voir fonction calcul_intersection)
###
def filtre_ENE_zone_choucas(file_geojson, file_zone_choucas, crs):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon, MultiLineString, Polygon, LineString
	import fiona
	import json
	layer_geojson_filtré = []
	#layer_geojson, liste_geocodage_multipoints, liste_geocodage_title, ENE_points, ENE_title_Dict, df = lecture_geojson(file_geojson)
	layer_geojson, liste_geocodage_multipoints, df = lecture_geojson(file_geojson, 'ponctuel')

	output_geojson_fname = file_geojson[0:len(file_geojson)-8]+"_post_filtre_zone_choucas.json"
	#print(type(layer_geojson))
	zone_choucas = zone_etude_choucas (file_zone_choucas)

	if crs == '2154':
		zone_choucas_lamber93 = zone_choucas.to_crs({'init': 'epsg:2154'})
		geojson_lamber93 = df.to_crs({'init': 'epsg:2154'})

	geojcounterpoint = 0
	for geoj in layer_geojson:
		#Point([e['geometry']['coordinates']]).intersects(Point([ (6.863581641809704, 45.456162302128035)]))
		
		geoj['properties']['in_context_zone'] = "false"
		
		if  (geoj['geometry']['type'] == "Point"):

			point_geoj = Point([geoj['geometry']['coordinates']])		

		if  (geoj['geometry']['type'] == "MultiLineString"):

			point_geoj = MultiLineString(geoj['geometry']['coordinates'])

		if  (geoj['geometry']['type'] == "LineString"):

			point_geoj = LineString(geoj['geometry']['coordinates'])
		

		if  (geoj['geometry']['type'] == "MultiPolygon"):

			point_geoj = MultiPolygon([geoj['geometry']['coordinates']])

		if  (geoj['geometry']['type'] == "Polygon"):

			point_geoj = Polygon([geoj['geometry']['coordinates']])

		
		
		#boole = zone_choucas.contains(point_geoj)
		boole = zone_choucas_lamber93.contains(point_geoj)
		

		if (boole.bool()):
			#print(geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], point_geoj, geoj['properties']['findName'] )
			geojcounterpoint = geojcounterpoint + 1
			geoj['properties']['in_context_zone'] = "true"
			layer_geojson_filtré.append(geoj)


	print("********************************************layer_geojson_filtré********************************************")
	print(layer_geojson_filtré)
	with open(output_geojson_fname, 'w') as outfile:
		json.dump(layer_geojson_filtré, outfile)

	return layer_geojson_filtré, output_geojson_fname


###
# Filtration des objets spatiaux (type ponctuel) géolocalisées hors contexte (zone choucas). Utilisé pour la phase de  l'intersection entres la trace GPS et les objets spatiaux (voir fonction Appariment Complexe)
###

def filtre_BDGeo_zone_choucas_ponctuel(file_geojson, file_zone_choucas, crs):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon
	import fiona

	layer_geojson_filtré = []

	layer_geojson, liste_geocodage_multipoints, df = lecture_geojson(file_geojson, 'ponctuel')



	zone_choucas = zone_etude_choucas (file_zone_choucas)

	if crs == '2154':
		zone_choucas_lamber93 = zone_choucas.to_crs({'init': 'epsg:2154'})
		geojson_lamber93 = df.to_crs({'init': 'epsg:2154'})

	geojcounterpoint = 0
	for geoj in layer_geojson:

		point_geoj = Point([geoj['geometry']['coordinates']])
		

		boole = zone_choucas_lamber93.contains(point_geoj)
		

		if (boole.bool()):

			geojcounterpoint = geojcounterpoint + 1
			layer_geojson_filtré.append(geoj)





	return layer_geojson_filtré
###
# Filtration des objets spatiaux (type lineaire) géolocalisées hors contexte (zone choucas). Utilisé pour la phase de  l'intersection entres la trace GPS et les objets spatiaux (voir fonction Appariment Complexe)
###
def filtre_BDGeo_zone_choucas_lineaire(file_geojson, file_zone_choucas, crs):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon, LineString
	import fiona

	layer_geojson_filtré = []

	layer_geojson, df = lecture_geojson(file_geojson, 'lineaire')


	zone_choucas = zone_etude_choucas (file_zone_choucas)

	if crs == '2154':
		zone_choucas_lamber93 = zone_choucas.to_crs({'init': 'epsg:2154'})
		geojson_lamber93 = df.to_crs({'init': 'epsg:2154'})

	geojcounterpoint = 0

	for geoj in layer_geojson:

		point_geoj = LineString(geoj['geometry']['coordinates'])
		

		boole = zone_choucas_lamber93.contains(point_geoj)
		

		if (boole.bool()):

			geojcounterpoint = geojcounterpoint + 1
			layer_geojson_filtré.append(geoj)


	


	return layer_geojson_filtré


###
# Filtration des objets spatiaux (type multilineaire) géolocalisées hors contexte (zone choucas). Utilisé pour la phase de  l'intersection entres la trace GPS et les objets spatiaux (voir fonction Appariment Complexe)
###
def filtre_BDGeo_zone_choucas_multilineaire(file_geojson, file_zone_choucas, crs):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon, LineString, MultiLineString
	import fiona

	layer_geojson_filtré = []
	
	layer_geojson, df = lecture_geojson(file_geojson, 'lineaire')


	
	zone_choucas = zone_etude_choucas (file_zone_choucas)

	if crs == '2154':
		zone_choucas_lamber93 = zone_choucas.to_crs({'init': 'epsg:2154'})
		geojson_lamber93 = df.to_crs({'init': 'epsg:2154'})

	geojcounterpoint = 0
	for geoj in layer_geojson:
		
		point_geoj = MultiLineString(geoj['geometry']['coordinates'])
		
		
		boole = zone_choucas_lamber93.contains(point_geoj)
		

		if (boole.bool()):
			
			geojcounterpoint = geojcounterpoint + 1
			layer_geojson_filtré.append(geoj)


	


	return layer_geojson_filtré

###
# Filtration des objets spatiaux (type surface) géolocalisées hors contexte (zone choucas). Utilisé pour la phase de  l'intersection entres la trace GPS et les objets spatiaux (voir fonction Appariment Complexe)
###
def filtre_BDGeo_zone_choucas_surface(file_geojson, file_zone_choucas, crs):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon, Polygon
	import fiona

	layer_geojson_filtré = []
	
	layer_geojson, df = lecture_geojson(file_geojson, 'surface')


	
	zone_choucas = zone_etude_choucas (file_zone_choucas)

	if crs == '2154':
		zone_choucas_lamber93 = zone_choucas.to_crs({'init': 'epsg:2154'})
		geojson_lamber93 = df.to_crs({'init': 'epsg:2154'})

	geojcounterpoint = 0



	for geoj in layer_geojson:
		for polygone in geoj['geometry']['coordinates']:
			try:
				p = Polygon(polygone)
				boole = zone_choucas_lamber93.contains(p)
				if (boole.bool()):

					
					geojcounterpoint = geojcounterpoint + 1
					layer_geojson_filtré.append(geoj)
			except Exception as e:
							#raise e
							#print(polygone)
							continue

		

		





	return layer_geojson_filtré



def calcul_intersection(gpx_fname, taile_buffer_track, geojson_fname, taile_buffer_geojson, intesection_strict, zone_choucas_filename):
	import geopandas as gpd
	from shapely.geometry import Point, MultiPoint, MultiPolygon, MultiLineString
	import fiona
	import json
	import shapely.speedups
	shapely.speedups.enable()

	


	df_gpx = gpx_transform_crs(gpx_fname, '4326', '2154')
	
	df_geojson, geojson_lamber93_fname=lecture_geojson_dataframe_transform_crs(geojson_fname, '2154')


	output_geojson_fname = geojson_lamber93_fname[0:len(geojson_fname)-7]+"resutltat_service1_buffer_trace_"+str(taile_buffer_track) +"m.geojson"
	

	layer_geojson, liste_geocodage_multipoints, df = lecture_geojson(geojson_lamber93_fname, 'ponctuel')

	
	geojson_filtré, output_geojson_fname_post_zone_choucas = filtre_ENE_zone_choucas(geojson_lamber93_fname,zone_choucas_filename, "2154")

	
	print("\nLe nombre de point dans le Geojson (toponymes representants les ENE) AVANT application du filtre de zone choucas : ", len(layer_geojson))
	print("\nLe nombre de point dans le Geojson (toponymes representants les ENE) APRES application du filtre de zone choucas : ", len(geojson_filtré))

	
	


	buffer_track_gps_lamber = buffer_fixe_shape_GPX_lamber(df_gpx,taile_buffer_track, gpx_fname)



	

	layer_geojson_2 = fiona.open(geojson_fname)

###
# intesection_strict = true : Ne pas établir de buffer autours des ENE
# intesection_strict = false : Etablir buffer autours des ENE
###
	if intesection_strict:

		Dict_Liste_appariment_trace_geojson = dict()
		
		count_apparié = 0
		count_non_apparié = 0
		
		
		i=0

		Liste_ENE_apparié = []
		print("id_point_trace", "id_ENE","gid_ENE" "ENE_title", "geometry_ene_geojson" , "ENE_findName")


		dict_ene_apparié_nonapparié = dict()

		for geoj in geojson_filtré:
			id_ene = geoj['properties']['id']
			dict_ene_apparié_nonapparié [id_ene]= list()
				
		#for point_trace in buffer_track_gps:
		for point_trace in buffer_track_gps_lamber:
			Boolean_appariment = False
			Liste_appariment_trace_geojson=[]
			geojcounterpoint = 0
			Liste_ENE =[]
			for geoj in geojson_filtré:

				if geoj['properties']['id'] not in Liste_ENE:
					Liste_ENE.append(geoj['properties']['id'])
				#Point([e['geometry']['coordinates']]).intersects(Point([ (6.863581641809704, 45.456162302128035)]))
				
				#point_geoj = Point([geoj['geometry']['coordinates']])

				if  (geoj['geometry']['type'] == "MultiLineString"):
					point_geoj = MultiLineString(geoj['geometry']['coordinates'])
		
				if  (geoj['geometry']['type'] == "Point"):
					point_geoj = Point([geoj['geometry']['coordinates']])


				geojcounterpoint = geojcounterpoint + 1
				
				
				if point_trace.intersects(point_geoj):
					Boolean_appariment = True
					L_tomporaire = dict_ene_apparié_nonapparié[geoj['properties']['id']]
					L_tomporaire.append(i)
					dict_ene_apparié_nonapparié[geoj['properties']['id']] = L_tomporaire

					#count_apparié = count_apparié+1
					Liste_appariment_trace_geojson.append((i, geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], point_geoj, geoj['properties']['findName'] ))
					if geoj['properties']['id'] not in Liste_ENE_apparié:
						Liste_ENE_apparié.append(geoj['properties']['id'])


					print(i, geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], geoj['geometry']['type'],  geoj['properties']['findName'] )


			if (Boolean_appariment == False):
				count_non_apparié = count_non_apparié +1
			if (Boolean_appariment == True):
				count_apparié = count_apparié+1
			
			Dict_Liste_appariment_trace_geojson[i]=Liste_appariment_trace_geojson
			i=i+1




	else:
		
		Dict_Liste_appariment_trace_geojson = dict()

		i=0
		geojcounterpoint = 0
		count_apparié = 0
		count_non_apparié = 0
		Liste_ENE_apparié = []
		print("id_point_trace", "id_ENE","gid_ENE" "ENE_title", "geometry_ene_geojson" , "ENE_findName")

		dict_ene_apparié_nonapparié = dict()

		for geoj in geojson_filtré:
			id_ene = geoj['properties']['id']
			dict_ene_apparié_nonapparié [id_ene]= list()

		#for point_trace in buffer_track_gps:
		for point_trace in buffer_track_gps_lamber:
			Boolean_appariment = False
			Liste_appariment_trace_geojson=[]
			geojcounterpoint = 0
			Liste_ENE =[]
			for geoj in geojson_filtré:

				if geoj['properties']['id'] not in Liste_ENE:
					Liste_ENE.append(geoj['properties']['id'])

				geojcounterpoint = geojcounterpoint + 1

				if  (geoj['geometry']['type'] == "MultiLineString"):
					point_geoj = MultiLineString(geoj['geometry']['coordinates'])
					point_geoj_buffer= point_geoj.buffer(taile_buffer_geojson) 
		
				if  (geoj['geometry']['type'] == "Point"):
					point_geoj = Point([geoj['geometry']['coordinates']])
					point_geoj_buffer= point_geoj.buffer(taile_buffer_geojson) 
				
				if point_trace.intersects(point_geoj_buffer):
					
					Boolean_appariment = True

					L_tomporaire = dict_ene_apparié_nonapparié[geoj['properties']['id']]
					L_tomporaire.append(i)
					dict_ene_apparié_nonapparié[geoj['properties']['id']] = L_tomporaire
					
					Liste_appariment_trace_geojson.append((i, geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], point_geoj, geoj['properties']['findName'] ))
					if geoj['properties']['id'] not in Liste_ENE_apparié:
						Liste_ENE_apparié.append(geoj['properties']['id'])


					#print(i, geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], point_geoj, geoj['properties']['findName'] )
					print(i, geoj['properties']['id'] ,geoj['properties']['gid'] ,geoj['properties']['title'], geoj['geometry']['type'], geoj['properties']['findName'] )
			
			if (Boolean_appariment == False):
				count_non_apparié = count_non_apparié +1
			if (Boolean_appariment == True):
				count_apparié = count_apparié+1
			Dict_Liste_appariment_trace_geojson[i]=Liste_appariment_trace_geojson
			i=i+1

	

	

	
	print("\n****************************************************************************Résultats**************************************************************************************************************\n")
	print("Configuration les tailles de buffers : Taille buffer trace : "+ str(taile_buffer_track)+"m\n", "Taille du buffer autours des ENE (buffer autour du toponyme issus du geocodage des ENE) : "+ str(taile_buffer_geojson) )
	print("Sur "+str(i) +" points", "nombre de points de la trace appariées : " + str(count_apparié), "nombre de points de la trace non appariées : " + str(count_non_apparié))
	print("Sur "+str(geojcounterpoint) +" entités spatiales nommées (ESN) dans le textes (geojson)", "nombre de ENE appariées : " + str(len(Liste_ENE_apparié)), "nombre de ENE non appariées : " + str((geojcounterpoint-len(Liste_ENE_apparié))))
	print("\n****************************************************************************Résultats**************************************************************************************************************\n")
	print ("Liste des ENE appariés : ",Liste_ENE_apparié)

	Set_ene = set(Liste_ENE)
	set_ene_apparié = set (Liste_ENE_apparié)
	set_ene_non_apparié = Set_ene  - set_ene_apparié

	print ("Liste des ENE non appariées sont : ",set_ene_non_apparié)
###
#enregistrement des résultats d'appariement dans le geojson 
###	
	
	f_geojson = open(geojson_lamber93_fname,'r')

	data_json = json.load(f_geojson)

	


	for e in dict_ene_apparié_nonapparié:

		for elem in data_json['features']:
			
			if elem['properties']['id'] == e:
				if (len(dict_ene_apparié_nonapparié[e]) != 0):
					elem['properties']['matching'] = 'true'
					elem['properties']['matched_points'] = dict_ene_apparié_nonapparié[e]
				else:
					elem['properties']['matching'] = 'false'
					elem['properties']['matched_points'] = dict_ene_apparié_nonapparié[e]
				

	with open(output_geojson_fname, 'w') as outfile:
		json.dump(data_json, outfile)

	return Dict_Liste_appariment_trace_geojson, dict_ene_apparié_nonapparié

def main():

	Liste_texte_trace = []


#	trace 2 : but_st_genix_col_de_vassieux_but_de_l_ai : ESN +ESNN
	gpx2 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/but_st_genix_col_de_vassieux_but_de_l_ai.gpx"
	#json2 = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).json"
	json2 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).json"
	#json2_out = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).geojson"
	json2_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).geojson"
	geojson2  = JSON_TO_GEOJSON(json2, json2_out)

	Liste_texte_trace.append((gpx2, json2_out))


	trace 3 : de_la_jasse_du_play_a_la_baraque_du_piso

	gpx3 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/de_la_jasse_du_play_a_la_baraque_du_piso.gpx"
	json3 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).json"
	#json3_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).geojson"
	json3_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).geojson"
	#geojson3  = JSON_TO_GEOJSON(json3, json3_out)

	Liste_texte_trace.append((gpx3, json3_out))

	#trace 4 : vallee_de_champoleon

	gpx4 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/vallee_de_champoleon.gpx"
	json4 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/Corrigee_Perdido_vallee_de_champoleon(ESN+ESNN).json"
	json4_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/Corrigee_Perdido_vallee_de_champoleon(ESN+ESNN).geojson"
	geojson4  = JSON_TO_GEOJSON(json4, json4_out)

	Liste_texte_trace.append((gpx4, json4_out))



	zone_choucas_filename = "/home/medad/Bureau/zoneEtude/limite_wgs84.shp"


	for trace_text in Liste_texte_trace:
		gpx = trace_text[0]
		geojson = trace_text[1]
		print("Appariment service 1 : \nTrace : ", gpx, "\n")
		print("Geojson : ", geojson, "\n")
		#for bufrer_trace in [0.00009,0.00018, 0.00036, 0.00045,0.0009,0.00135,0.0018,0.00225,0.0027]:
		#for bufrer_trace in [10, 20, 40, 50, 100, 150, 200, 250, 300]:
		for bufrer_trace in [10, 20, 30,40, 50, 60, 70, 80, 90, 100]:	
			print("****************************Appariment texte trace (buffer trace = "+str(bufrer_trace)+"m) : texte representée par liste ENE geojson***********************")
			Dict_Liste_appariment_trace_geojson, dict_ene_apparié_nonapparié = calcul_intersection(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename)
			for e in Dict_Liste_appariment_trace_geojson:
				print(e,Dict_Liste_appariment_trace_geojson[e])

			for e in dict_ene_apparié_nonapparié:
				print(e,dict_ene_apparié_nonapparié[e])
			
			# print("appariment BD Geographique (OSM) avec la trace : type d'objets complexe (ponctuel, lineaire, surface) ")
			# #appariement_objet_complexe(gpx_fname, taile_buffer_track, geojson_fname, taile_buffer_geojson, intesection_strict, zone_choucas_filename, ponctuel, lineaire, surface):
			
			# #appariement_objet_complexe(gpx, bufrer_trace, geojson, 0.00045, True, zone_choucas_filename, True, False, False)
			# print("\n***********************************Ponctuel********************************************************* \n")
			# appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, True, False, False)
			# print("\n***********************************Lineaire********************************************************* \n")
			# appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, False, True, False)
			# #appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, False, False, True)



#Check Geometry
def isvalid(geom):
    try:
        shape(geom)
        return 1
    except:
        return 0


def appariement_objet_complexe(gpx_fname, taile_buffer_track, geojson_fname, taile_buffer_geojson, intesection_strict, zone_choucas_filename, ponctuel, lineaire, surface):
	import geopandas as gpd
	import json
	import pandas as pd
	from shapely.geometry import shape 
	from shapely.geometry import Point, MultiPoint, MultiPolygon, LineString, Polygon, MultiLineString
	import fiona


	import shapely.speedups
	shapely.speedups.enable()
	
	print("ponctuel : ", ponctuel)
	print("lineaire : ", lineaire)
	print("surface : ", surface)


	
	df_gpx = gpx_transform_crs(gpx_fname, '4326', '2154')	
	#track_gps, layer_gpx, trace_multipoint, liste_points = lecture_gpx(gpx_fname)

	buffer_track_gps_lamber = buffer_fixe_shape_GPX_lamber(df_gpx,taile_buffer_track, gpx_fname)

	

	


	dimention = [ponctuel, lineaire, surface]
	if intesection_strict:
		
		Dict_Liste_appariment_trace_geojson = dict()
		
		
		if dimention[0] == True:

			df_geojson, geojson_lamber93_fname=lecture_geojson_dataframe_transform_crs("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_points.geojson", '2154')
			# layer_geojson, liste_geocodage_multipoints, liste_geocodage_title, ENE_points, ENE_title_Dict, df = lecture_geojson(geojson_lamber93_fname)
			#layer_geojson, liste_geocodage_multipoints, df = lecture_geojson(geojson_lamber93_fname)
			
			geojson_filtré = filtre_BDGeo_zone_choucas_ponctuel(geojson_lamber93_fname,zone_choucas_filename, "2154")
			#print(geojson_filtré)
			
			print("\nLe nombre de point dans le Geojson AVANT application du filtre de zone choucas : ", len(df_geojson))
			print("\nLe nombre de point dans le Geojson APRES application du filtre de zone choucas : ", len(geojson_filtré))


			#layer = fiona.open("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_points.geojson")
			i = 0
			#for point_trace in buffer_track_gps:
			for point_trace in buffer_track_gps_lamber:
				#print(point_trace)
				#for e in layer_geojson:
				for e in geojson_filtré:

					point_geoj = Point([e['geometry']['coordinates']])
					#print(point_trace, point_geoj)

					if point_trace.intersects(point_geoj):
						print(i,e['properties']['name'],' : ',e['geometry']['coordinates'])

				i = i+1			

		
		if dimention[1] == True:
			#layer = fiona.open("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_lines.geojson")
			i = 0

			#df_geojson, geojson_lamber93_fname=lecture_geojson_dataframe_transform_crs("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_lines.geojson", '2154')
			df_geojson, geojson_lamber93_fname=lecture_geojson_dataframe_transform_crs("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_multilinestrings.geojson", '2154')

			
			geojson_filtré = filtre_BDGeo_zone_choucas_multilineaire(geojson_lamber93_fname,zone_choucas_filename, "2154")
			
			
			print("\nLe nombre de point dans le Geojson AVANT application du filtre de zone choucas : ", len(df_geojson))
			print("\nLe nombre de point dans le Geojson APRES application du filtre de zone choucas : ", len(geojson_filtré))

			#for point_trace in buffer_track_gps:
			for point_trace in buffer_track_gps_lamber:
				#print(point_trace)
				for e in geojson_filtré:

					#point_geoj = LineString(e['geometry']['coordinates'])
					point_geoj = MultiLineString(e['geometry']['coordinates'])


					if point_trace.intersects(point_geoj):
						#print('Point de la trace N :',i,e['properties']['name'],' : ',e['geometry']['coordinates'])
						print('Point de la trace N :',i, e['properties'])

				i = i+1	

		
		if dimention[2] == True:


			df_geojson, geojson_lamber93_fname=lecture_geojson_dataframe_transform_crs("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_multipolygons.geojson", '2154')
			# layer_geojson, liste_geocodage_multipoints, liste_geocodage_title, ENE_points, ENE_title_Dict, df = lecture_geojson(geojson_lamber93_fname)
			#layer_geojson, liste_geocodage_multipoints, df = lecture_geojson(geojson_lamber93_fname)
			geojson_filtré = filtre_BDGeo_zone_choucas_surface(geojson_lamber93_fname,zone_choucas_filename, "2154")
			#print(geojson_filtré)
			
			print("\nLe nombre de point dans le Geojson AVANT application du filtre de zone choucas : ", len(df_geojson))
			print("\nLe nombre de point dans le Geojson APRES application du filtre de zone choucas : ", len(geojson_filtré))

			#layer = fiona.open("/home/medad/Bureau/Corpus-Gold-standart/BD_geos_zone_choucas/osm_zone_choucas_multipolygons.geojson")
			i = 0
			#for point_trace in buffer_track_gps:
			for point_trace in buffer_track_gps_lamber:
				#print(point_trace)
				for e in geojson_filtré:
					for polygone in e['geometry']['coordinates']:
						#print(polygone)
						try:
							p = Polygon(polygone)
							p_valid = p.buffer(0)
							print(point_trace, p)
							if point_trace.intersects(p):
								print(i,e['properties']['name'],' : ','intersection avec le polygone : ',p, 'un polygone de la surface representée par le multipolygone : ',e['geometry']['coordinates'])
						except Exception as e:
							#raise e
							#print(polygone)
							continue
					#point_geoj = MultiPolygon(e['geometry']['coordinates'])
					#print(point_geoj)

						

				i = i+1			
		
		


def Service_2(file_geojson_sortie_service1, fname_trace_gpx):
	import json
	from collections import OrderedDict

	f_geojson  =  open(file_geojson_sortie_service1, 'r')

	data_geojson = json.load(f_geojson)

	dict_sortie_service1 = dict()
	
	for e in data_geojson['features']:
		identif = e['properties']['id']
		Liste_matched_point = e['properties']['matched_points']
		dict_sortie_service1[identif] = Liste_matched_point

	un_compteur = -1
	pos = -1

	print(dict_sortie_service1)

	for e in dict_sortie_service1:
		print(e, dict_sortie_service1[e])
		un_compteur = un_compteur +1
		pos+=1

		#tester si le matched points est vide
		if 	(len(dict_sortie_service1[e]) == 0):
			# cas premier element
			if un_compteur == 0:

				listForm = list(dict_sortie_service1.keys())
				
				elem_next_key = listForm[pos+1]
				
				elem_next = dict_sortie_service1[elem_next_key]

				
				#elem_next, key = dict_sortie_service1._OrderedDict__map[e]

				#elem_prev_matched_point = dict_sortie_service1[elem_prev]
				

				#elem_next_matched_point = dict_sortie_service1[elem_next]

				premier_point = 0

				dernier_point = elem_next[0]

				for i in range(premier_point, dernier_point):
					dict_sortie_service1[e].append(i)
				print(dict_sortie_service1[e])
			#cas dernier element		
			if un_compteur == len(dict_sortie_service1) -1:

				listForm = list(dict_sortie_service1.values())
				elem_prev = dict_sortie_service1[listForm[pos-1]]
				#elem_prev,  key = dict_sortie_service1._OrderedDict__map[e]

				#elem_prev_matched_point = dict_sortie_service1[elem_prev]
				

				premier_point = elem_prev[len(elem_prev)-1]

				dernier_point = "le_dernier_point de la trace"

				for i in range(premier_point, dernier_point):
					dict_sortie_service1[e].append(i)

			#cas d'un element au milieu		
			if (un_compteur != len(dict_sortie_service1) -1) and (un_compteur != 0):

				elem_prev_tempo = dict_sortie_service1[listForm[pos-1]]
				print(elem_prev_tempo)
				#chercher le prochain element dont le matched_points !=0
				pos_next = pos
				while (len(elem_prev_tempo) == 0):
					pos_next = pos_next + 1



				# elem_prev = dict_sortie_service1[listForm[pos-1]]
				# elem_next = dict_sortie_service1[listForm[pos+1]]
				elem_prev = dict_sortie_service1[listForm[position_elemen_precedent_apparié]]
				elem_next = dict_sortie_service1[listForm[pos_next]]

				print(pos_next, listForm[pos_next],elem_next)
				
				#elem_prev, elem_next, key = dict_sortie_service1._OrderedDict__map[e]

				#elem_prev_matched_point = dict_sortie_service1[elem_prev]
				#elem_next_matched_point = dict_sortie_service1[elem_next]

				premier_point = elem_prev[len(elem_prev)-1]
				print(premier_point)

				dernier_point = elem_next[0]

				for i in range(premier_point, dernier_point):
					dict_sortie_service1[e].append(i)

		else:
			position_elemen_precedent_apparié = pos


	

	for elemn in dict_sortie_service1:
		data_geojson['features'][elemn]['matched_points']= dict_sortie_service1[elemn]

	print(data_geojson)

	return dict_sortie_service1
	# Dict_Liste_appariment_trace_geojson, dict_ene_apparié_nonapparié = calcul_intersection(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename)
	
	# for e in dict_ene_apparié_nonapparié:
	# 	print(e,dict_ene_apparié_nonapparié[e])








Liste_texte_trace = []
# #trace 2 : but_st_genix_col_de_vassieux_but_de_l_ai : ESN
# gpx2 = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/but_st_genix_col_de_vassieux_but_de_l_ai.gpx"
# json2 = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai.json"
# json2_out = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai.geojson"
# geojson2  = JSON_TO_GEOJSON(json2, json2_out)

# Liste_texte_trace.append((gpx2, json2_out))

#trace 2 : but_st_genix_col_de_vassieux_but_de_l_ai : ESN +ESNN
# gpx2 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/but_st_genix_col_de_vassieux_but_de_l_ai.gpx"
# #json2 = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).json"
# json2 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).json"
# #json2_out = "/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).geojson"
# json2_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/but_st_genix_col_de_vassieux_but_de_l_ai/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).geojson"
# geojson2  = JSON_TO_GEOJSON(json2, json2_out)

# Liste_texte_trace.append((gpx2, json2_out))


#trace 3 : de_la_jasse_du_play_a_la_baraque_du_piso

gpx3 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/de_la_jasse_du_play_a_la_baraque_du_piso.gpx"
json3 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).json"
#json3_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).geojson"
json3_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/de_la_jasse_du_play_a_la_baraque_du_piso/Corrigee_Perdido_de_la_jasse_du_play_a_la_baraque_du_piso(ESN+ESNN).geojson"
#geojson3  = JSON_TO_GEOJSON(json3, json3_out)

Liste_texte_trace.append((gpx3, json3_out))

# #trace 4 : vallee_de_champoleon

# gpx4 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/vallee_de_champoleon.gpx"
# json4 = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/Corrigee_Perdido_vallee_de_champoleon(ESN+ESNN).json"
# json4_out = "/home/medad/Bureau/Corpus-Gold-standart/appariment_processing/Evaluation_service_1/vallee_de_champoleon/Corrigee_Perdido_vallee_de_champoleon(ESN+ESNN).geojson"
# geojson4  = JSON_TO_GEOJSON(json4, json4_out)

# Liste_texte_trace.append((gpx4, json4_out))



zone_choucas_filename = "/home/medad/Bureau/zoneEtude/limite_wgs84.shp"
#calcul_intersection(gpx_fname, taile_buffer_track, geojson_fname, taile_buffer_geojson, intesection_strict)
#calcul_intersection(gpx, 0.0027, geojson, 0.00045, True)
#calcul_intersection(gpx, 0.0027, geojson, 1, False)


# d = Service_2("/home/medad/Bureau/Corpus-Gold-standart/Texts+traces/but_st_genix_col_de_vassieux_but_de_l_ai/annotation_ESNE/Corrigee_ENE_traversé_JOIN_PERDIDO_but_st_genix_col_de_vassieux_but_de_l_ai(ESN+ESNN annotées).resutltat_service1.geojson", gpx2)

# print(d)
for trace_text in Liste_texte_trace:
	gpx = trace_text[0]
	geojson = trace_text[1]
	print("Appariment service 1 : \nTrace : ", gpx, "\n")
	print("Geojson : ", geojson, "\n")
	#for bufrer_trace in [0.00009,0.00018, 0.00036, 0.00045,0.0009,0.00135,0.0018,0.00225,0.0027]:
	#for bufrer_trace in [10, 20, 40, 50, 100, 150, 200, 250, 300]:
	for bufrer_trace in [10, 20, 30,40, 50, 60, 70, 80, 90, 100]:	
		print("****************************Appariment texte trace (buffer trace = "+str(bufrer_trace)+"m) : texte representée par liste ENE geojson***********************")
		Dict_Liste_appariment_trace_geojson, dict_ene_apparié_nonapparié = calcul_intersection(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename)
		# for e in Dict_Liste_appariment_trace_geojson:
		# 	print(e,Dict_Liste_appariment_trace_geojson[e])

		# for e in dict_ene_apparié_nonapparié:
		# 	print(e,dict_ene_apparié_nonapparié[e])
		
		# print("appariment BD Geographique (OSM) avec la trace : type d'objets complexe (ponctuel, lineaire, surface) ")
		# #appariement_objet_complexe(gpx_fname, taile_buffer_track, geojson_fname, taile_buffer_geojson, intesection_strict, zone_choucas_filename, ponctuel, lineaire, surface):
		
		# #appariement_objet_complexe(gpx, bufrer_trace, geojson, 0.00045, True, zone_choucas_filename, True, False, False)
		# print("\n***********************************Ponctuel********************************************************* \n")
		# appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, True, False, False)
		# print("\n***********************************Lineaire********************************************************* \n")
		# appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, False, True, False)
		# #appariement_objet_complexe(gpx, bufrer_trace, geojson, 0, True, zone_choucas_filename, False, False, True)
