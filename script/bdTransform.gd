extends Node

var db : SQLite
var db_name = "res://transforme.db"

func _ready():
	print("=== DÉBUT DU SCRIPT bdTransform.gd ===")
	
	# Test de l'extension SQLite
	if SQLite == null:
		print("ERREUR: Extension SQLite non trouvée!")
		return
	else:
		print("✓ Extension SQLite détectée")
	
	print("Initialisation de la base de données...")
	init_database()
	
	print("=== BASE DE DONNÉES INITIALISÉE ===")
	print("Tables créées et prêtes à l'emploi.")
	
	# Créer des données de test pour vérifier l'export
	print("\n=== CRÉATION DE DONNÉES DE TEST ===")
	create_sample_data()
	
	print("\n=== EXPORT VERS CSV ===")
	export_database_to_csv()

func init_database():
	print("=== INITIALISATION DE LA BASE DE DONNÉES ===")
	print("Chemin de la base de données : ", db_name)
	
	db = SQLite.new()
	print("Instance SQLite créée")
	
	db.path = db_name
	print("Chemin défini : ", db.path)
	
	var open_result = db.open_db()
	if open_result:
		print("✓ Base de données ouverte avec succès")
	else:
		print("✗ Erreur lors de l'ouverture de la base de données")
		return
	
	print("--- Création de la table Transforme ---")
	# Création de la table Transforme
	var table_transforme_query = """
	CREATE TABLE IF NOT EXISTS Transforme (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		position_x REAL NOT NULL,
		position_y REAL NOT NULL,
		position_z REAL NOT NULL,
		rotation_x REAL NOT NULL,
		rotation_y REAL NOT NULL,
		rotation_z REAL NOT NULL,
		scale_x REAL NOT NULL,
		scale_y REAL NOT NULL,
		scale_z REAL NOT NULL
	);
	"""
	
	var transforme_result = db.query(table_transforme_query)
	if transforme_result != false:
		print("✓ Table 'Transforme' créée ou vérifiée")
	else:
		print("✗ Erreur lors de la création de la table 'Transforme'")
	
	print("--- Création de la table Materiau ---")
	# Création de la table Materiau
	var table_materiau_query = """
	CREATE TABLE IF NOT EXISTS Materiau (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		nom TEXT NOT NULL,
		poids REAL NOT NULL,
		opacite REAL NOT NULL,
		couleur TEXT NOT NULL
	);
	"""
	
	var materiau_result = db.query(table_materiau_query)
	if materiau_result != false:
		print("✓ Table 'Materiau' créée ou vérifiée")
	else:
		print("✗ Erreur lors de la création de la table 'Materiau'")
	
	print("--- Création de la table Objet ---")
	# Création de la table Objet
	var table_objet_query = """
	CREATE TABLE IF NOT EXISTS Objet (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		nom TEXT NOT NULL,
		transforme_id INTEGER NOT NULL,
		materiau_id INTEGER NOT NULL,
		sur_id INTEGER,
		FOREIGN KEY (transforme_id) REFERENCES Transforme(id),
		FOREIGN KEY (materiau_id) REFERENCES Materiau(id),
		FOREIGN KEY (sur_id) REFERENCES Sur(id)
	);
	"""
	
	var objet_result = db.query(table_objet_query)
	if objet_result != false:
		print("✓ Table 'Objet' créée ou vérifiée")
	else:
		print("✗ Erreur lors de la création de la table 'Objet'")
	
	print("--- Création de la table Sur ---")
	# Création de la table Sur
	var table_sur_query = """
	CREATE TABLE IF NOT EXISTS Sur (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		objet_id INTEGER NOT NULL,
		texte TEXT NOT NULL,
		FOREIGN KEY (objet_id) REFERENCES Objet(id)
	);
	"""
	
	var sur_result = db.query(table_sur_query)
	if sur_result != false:
		print("✓ Table 'Sur' créée ou vérifiée")
	else:
		print("✗ Erreur lors de la création de la table 'Sur'")
	
	print("=== INITIALISATION TERMINÉE ===")
	print("Toutes les tables ont été créées ou vérifiées avec succès")

func save_transform(rigidbody: RigidBody3D, materiau_id: int = 1, sur_id: int = -1):
	var transform = rigidbody.transform
	var position = transform.origin
	var rotation = rigidbody.rotation
	var scale = transform.basis.get_scale()
	
	# Insertion dans la table Transforme
	var insert_transform_query = """
	INSERT INTO Transforme (position_x, position_y, position_z, 
							rotation_x, rotation_y, rotation_z,
							scale_x, scale_y, scale_z)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
	"""
	
	var transform_values = [
		position.x, position.y, position.z,
		rotation.x, rotation.y, rotation.z,
		scale.x, scale.y, scale.z
	]
	
	db.query_with_bindings(insert_transform_query, transform_values)
	
	# Récupération de l'ID de la transformation insérée
	var transform_id = db.last_insert_rowid
	
	# Insertion dans la table Objet avec les clés étrangères
	var insert_objet_query
	var objet_values
	
	if sur_id > 0:
		insert_objet_query = """
		INSERT INTO Objet (nom, transforme_id, materiau_id, sur_id)
		VALUES (?, ?, ?, ?);
		"""
		objet_values = [rigidbody.name, transform_id, materiau_id, sur_id]
	else:
		insert_objet_query = """
		INSERT INTO Objet (nom, transforme_id, materiau_id)
		VALUES (?, ?, ?);
		"""
		objet_values = [rigidbody.name, transform_id, materiau_id]
	
	db.query_with_bindings(insert_objet_query, objet_values)
	
	var sur_info = " (sur_id: " + str(sur_id) + ")" if sur_id > 0 else ""
	print("Transform et Objet sauvegardés pour : ", rigidbody.name, " (transform_id: ", transform_id, ", materiau_id: ", materiau_id, ")", sur_info)

func get_all_rigidbodies(node, list):
	if node is RigidBody3D:
		list.append(node)
		
	for child in node.get_children():
		get_all_rigidbodies(child, list)

func save_all_rigidbodies():
	print("=== SAUVEGARDE DE TOUS LES RIGIDBODY ===")
	
	var rigidbodies = [] 
	get_all_rigidbodies(get_tree().get_root(), rigidbodies)
	
	if rigidbodies.size() == 0:
		print("Aucun RigidBody trouvé dans la scène")
		return
	
	for body in rigidbodies:
		print("RigidBody trouvé : ", body.name)
		# Assigner un matériau basé sur le nom de l'objet
		var materiau_id = get_materiau_id_for_object(body.name)
		save_transform(body, materiau_id)
	
	print("✓ ", rigidbodies.size(), " objets sauvegardés dans la base de données")

func load_transforms():
	var select_query = """
	SELECT o.id as objet_id, o.nom, o.transforme_id, o.materiau_id,
		   t.position_x, t.position_y, t.position_z,
		   t.rotation_x, t.rotation_y, t.rotation_z,
		   t.scale_x, t.scale_y, t.scale_z,
		   m.nom as materiau_nom, m.poids, m.opacite, m.couleur
	FROM Objet o
	JOIN Transforme t ON o.transforme_id = t.id
	JOIN Materiau m ON o.materiau_id = m.id
	ORDER BY o.id DESC;
	"""
	var result = db.query(select_query)
	
	for row in result:
		print("Objet ID: ", row["objet_id"], " - Nom: ", row["nom"], " (Transform ID: ", row["transforme_id"], ", Matériau ID: ", row["materiau_id"], ")")
		print("  Position: (", row["position_x"], ", ", row["position_y"], ", ", row["position_z"], ")")
		print("  Rotation: (", row["rotation_x"], ", ", row["rotation_y"], ", ", row["rotation_z"], ")")
		print("  Scale: (", row["scale_x"], ", ", row["scale_y"], ", ", row["scale_z"], ")")
		print("  Matériau: ", row["materiau_nom"], " (poids: ", row["poids"], ", opacité: ", row["opacite"], ", couleur: ", row["couleur"], ")")
		print("---")
	
	return result

func load_objets():
	var select_query = "SELECT * FROM Objet ORDER BY id DESC;"
	var result = db.query(select_query)
	
	for row in result:
		print("Objet ID: ", row["id"], " - Nom: ", row["nom"], " -> Transform ID: ", row["transforme_id"], ", Matériau ID: ", row["materiau_id"])
	
	return result

func save_materiau(nom: String, poids: float, opacite: float, couleur: String):
	var insert_materiau_query = """
	INSERT INTO Materiau (nom, poids, opacite, couleur)
	VALUES (?, ?, ?, ?);
	"""
	
	var values = [nom, poids, opacite, couleur]
	
	db.query_with_bindings(insert_materiau_query, values)
	print("Matériau sauvegardé : ", nom, " (poids: ", poids, ", opacité: ", opacite, ", couleur: ", couleur, ")")

func load_materiaux():
	var select_query = "SELECT * FROM Materiau ORDER BY id DESC;"
	var result = db.query(select_query)
	
	for row in result:
		print("Matériau ID: ", row["id"], " - Nom: ", row["nom"])
		print("  Poids: ", row["poids"])
		print("  Opacité: ", row["opacite"])
		print("  Couleur: ", row["couleur"])
		print("---")
	
	return result

func save_sur(objet_id: int, texte: String):
	var insert_sur_query = """
	INSERT INTO Sur (objet_id, texte)
	VALUES (?, ?);
	"""
	
	var values = [objet_id, texte]
	
	db.query_with_bindings(insert_sur_query, values)
	print("Donnée Sur sauvegardée : objet_id=", objet_id, ", texte='", texte, "'")

func load_surs():
	var select_query = "SELECT * FROM Sur ORDER BY id DESC;"
	var result = db.query(select_query)
	
	for row in result:
		print("Sur ID: ", row["id"], " - Objet ID: ", row["objet_id"])
		print("  Texte: ", row["texte"])
		print("---")
	
	return result

func create_default_materials():
	print("=== CRÉATION DES MATÉRIAUX PAR DÉFAUT ===")
	
	# Vérifier si des matériaux existent déjà
	var check_query = "SELECT COUNT(*) as count FROM Materiau;"
	var result = db.query(check_query)
	print("Résultat de la vérification des matériaux: ", result)
	
	var need_to_create = false
	
	if result is Array and result.size() > 0:
		var count = result[0]["count"]
		print("Nombre de matériaux existants: ", count)
		if count == 0:
			need_to_create = true
	else:
		# Si la requête ne retourne pas un Array, assumons qu'il faut créer les matériaux
		print("Résultat de requête inattendu, création des matériaux par défaut")
		need_to_create = true
	
	if need_to_create:
		print("Création des matériaux par défaut...")
		save_materiau("Bois", 0.8, 1.0, "marron")
		save_materiau("Pierre", 2.5, 1.0, "gris")
		save_materiau("Metal", 7.8, 1.0, "argent")
		save_materiau("Defaut", 1.0, 1.0, "blanc")
		print("✓ Matériaux par défaut créés")
	else:
		print("Les matériaux existent déjà, pas besoin de les créer")

func get_materiau_id_for_object(object_name: String) -> int:
	# Logique simple pour assigner des matériaux basés sur le nom
	var materiau_name = "Defaut"
	
	if "Bois" in object_name or "Violet" in object_name:
		materiau_name = "Bois"
	elif "roche" in object_name or "Gris" in object_name:
		materiau_name = "Pierre"
	elif "Metal" in object_name:
		materiau_name = "Metal"
	
	# Récupérer l'ID du matériau
	var query = "SELECT id FROM Materiau WHERE nom = ? LIMIT 1;"
	var result = db.query_with_bindings(query, [materiau_name])
	
	if result is Array and result.size() > 0:
		return result[0]["id"]
	else:
		# Retourner l'ID du matériau par défaut (devrait être 4)
		var default_query = "SELECT id FROM Materiau WHERE nom = 'Defaut' LIMIT 1;"
		var default_result = db.query(default_query)
		if default_result is Array and default_result.size() > 0:
			return default_result[0]["id"]
		else:
			return 1  # Fallback au premier matériau

func pad_string(text: String, length: int) -> String:
	var result = text
	while result.length() < length:
		result += " "
	if result.length() > length:
		result = result.substr(0, length)
	return result

func display_all_database_tables():
	print("================== AFFICHAGE COMPLET DE LA BASE DE DONNÉES ==================")
	
	# Affichage de la table Materiau
	print("\n+==============================================================================+")
	print("|                                 TABLE MATERIAU                              |")
	print("+==============================================================================+")
	var materiaux_result = db.query("SELECT * FROM Materiau ORDER BY id;")
	print("DEBUG: Résultat query Materiau = ", materiaux_result)
	
	if materiaux_result is Array and materiaux_result.size() > 0:
		print("+------+----------------+--------+----------+----------------+")
		print("| ID   | NOM            | POIDS  | OPACITE  | COULEUR        |")
		print("+------+----------------+--------+----------+----------------+")
		for row in materiaux_result:
			var id_str = pad_string(str(row["id"]), 4)
			var nom_str = pad_string(str(row["nom"]), 14)
			var poids_str = pad_string(str(row["poids"]), 6)
			var opacite_str = pad_string(str(row["opacite"]), 8)
			var couleur_str = pad_string(str(row["couleur"]), 14)
			print("| ", id_str, " | ", nom_str, " | ", poids_str, " | ", opacite_str, " | ", couleur_str, " |")
		print("+------+----------------+--------+----------+----------------+")
	else:
		print("|                          AUCUN MATÉRIAU TROUVÉ                             |")
		print("+-----------------------------------------------------------------------------+")
	
	# Affichage de la table Transforme
	print("\n+=====================================================================================================+")
	print("|                                        TABLE TRANSFORME                                            |")
	print("+=====================================================================================================+")
	var transforme_result = db.query("SELECT * FROM Transforme ORDER BY id;")
	print("DEBUG: Résultat query Transforme = ", transforme_result)
	
	if transforme_result is Array and transforme_result.size() > 0:
		print("+----+----------+----------+----------+----------+----------+----------+--------+--------+--------+")
		print("| ID | POS_X    | POS_Y    | POS_Z    | ROT_X    | ROT_Y    | ROT_Z    | SCL_X  | SCL_Y  | SCL_Z  |")
		print("+----+----------+----------+----------+----------+----------+----------+--------+--------+--------+")
		for row in transforme_result:
			var id_str = pad_string(str(row["id"]), 2)
			var pos_x_str = pad_string("%.2f" % row["position_x"], 8)
			var pos_y_str = pad_string("%.2f" % row["position_y"], 8)
			var pos_z_str = pad_string("%.2f" % row["position_z"], 8)
			var rot_x_str = pad_string("%.2f" % row["rotation_x"], 8)
			var rot_y_str = pad_string("%.2f" % row["rotation_y"], 8)
			var rot_z_str = pad_string("%.2f" % row["rotation_z"], 8)
			var scl_x_str = pad_string("%.2f" % row["scale_x"], 6)
			var scl_y_str = pad_string("%.2f" % row["scale_y"], 6)
			var scl_z_str = pad_string("%.2f" % row["scale_z"], 6)
			print("| ", id_str, " | ", pos_x_str, " | ", pos_y_str, " | ", pos_z_str, " | ", rot_x_str, " | ", rot_y_str, " | ", rot_z_str, " | ", scl_x_str, " | ", scl_y_str, " | ", scl_z_str, " |")
		print("+----+----------+----------+----------+----------+----------+----------+--------+--------+--------+")
	else:
		print("|                                    AUCUNE TRANSFORMATION TROUVÉE                                  |")
		print("+---------------------------------------------------------------------------------------------------+")
	
	# Affichage de la table Objet
	print("\n+================================================================+")
	print("|                        TABLE OBJET                            |")
	print("+================================================================+")
	var objet_result = db.query("SELECT * FROM Objet ORDER BY id;")
	print("DEBUG: Résultat query Objet = ", objet_result)
	
	if objet_result is Array and objet_result.size() > 0:
		print("+------+--------------------+--------------+--------------+----------+")
		print("| ID   | NOM                | TRANSFORM_ID | MATERIAU_ID  | SUR_ID   |")
		print("+------+--------------------+--------------+--------------+----------+")
		for row in objet_result:
			var id_str = pad_string(str(row["id"]), 4)
			var nom_str = pad_string(str(row["nom"]), 18)
			var transform_id_str = pad_string(str(row["transforme_id"]), 12)
			var materiau_id_str = pad_string(str(row["materiau_id"]), 12)
			var sur_id_str = pad_string(str(row.get("sur_id", "NULL")) if row.has("sur_id") and row["sur_id"] != null else "NULL", 8)
			print("| ", id_str, " | ", nom_str, " | ", transform_id_str, " | ", materiau_id_str, " | ", sur_id_str, " |")
		print("+------+--------------------+--------------+--------------+----------+")
	else:
		print("|                      AUCUN OBJET TROUVÉ                      |")
		print("+---------------------------------------------------------------+")
	
	# Affichage de la table Sur
	print("\n+================================================================+")
	print("|                        TABLE SUR                              |")
	print("+================================================================+")
	var sur_result = db.query("SELECT * FROM Sur ORDER BY id;")
	print("DEBUG: Résultat query Sur = ", sur_result)
	
	if sur_result is Array and sur_result.size() > 0:
		print("+------+------------+------------------------------------------+")
		print("| ID   | OBJET_ID   | TEXTE                                    |")
		print("+------+------------+------------------------------------------+")
		for row in sur_result:
			var id_str = pad_string(str(row["id"]), 4)
			var objet_id_str = pad_string(str(row["objet_id"]), 10)
			var texte_str = pad_string(str(row["texte"]), 40)
			print("| ", id_str, " | ", objet_id_str, " | ", texte_str, " |")
		print("+------+------------+------------------------------------------+")
	else:
		print("|                      AUCUNE DONNÉE SUR TROUVÉE               |")
		print("+---------------------------------------------------------------+")
	
	# Affichage d'un résumé
	var total_materiaux = materiaux_result.size() if materiaux_result is Array else 0
	var total_transforme = transforme_result.size() if transforme_result is Array else 0  
	var total_objets = objet_result.size() if objet_result is Array else 0
	var total_surs = sur_result.size() if sur_result is Array else 0
	
	print("\n+===============================+")
	print("|           RÉSUMÉ              |")
	print("+===============================+")
	print("| Matériaux  : ", pad_string(str(total_materiaux), 13), " |")
	print("| Transforme : ", pad_string(str(total_transforme), 13), " |")
	print("| Objets     : ", pad_string(str(total_objets), 13), " |")
	print("| Sur        : ", pad_string(str(total_surs), 13), " |")
	print("+===============================+")
	print("================== FIN DE L'AFFICHAGE DE LA BASE DE DONNÉES ==================")

func export_database_to_csv():
	print("================== EXPORT DES TABLES EN CSV ==================")
	
	if db == null:
		print("✗ ERREUR: Base de données non initialisée!")
		return
	
	# Création du dossier CSV s'il n'existe pas
	var csv_dir = "res://csv/"
	if not DirAccess.dir_exists_absolute(csv_dir):
		var dir = DirAccess.open("res://")
		if dir:
			var result = dir.make_dir("csv")
			if result == OK:
				print("✓ Dossier CSV créé : ", csv_dir)
			else:
				print("✗ Erreur lors de la création du dossier CSV, code: ", result)
		else:
			print("✗ Impossible d'accéder au dossier racine")
	else:
		print("✓ Dossier CSV existe déjà : ", csv_dir)
	
	print("✓ Base de données disponible")
	
	# Export de la table Materiau
	print("Export de la table Materiau...")
	# Essayons select_rows avec des conditions vides
	var materiaux_result = db.select_rows("Materiau", "", ["*"])
	print("Résultat select_rows Materiau: ", materiaux_result)
	print("Type de résultat: ", typeof(materiaux_result))
	
	# Essayons aussi avec query comme les autres fonctions
	var materiau_query = "SELECT * FROM Materiau ORDER BY id;"
	var materiaux_result_query = db.query(materiau_query)
	print("Résultat query Materiau: ", materiaux_result_query)
	print("Type de résultat query: ", typeof(materiaux_result_query))
	
	var materiau_csv = "ID,NOM,POIDS,OPACITE,COULEUR\n"
	
	if materiaux_result is Array and materiaux_result.size() > 0:
		for row in materiaux_result:
			materiau_csv += str(row["id"]) + "," + str(row["nom"]) + "," + str(row["poids"]) + "," + str(row["opacite"]) + "," + str(row["couleur"]) + "\n"
		print("✓ ", materiaux_result.size(), " matériaux trouvés")
	else:
		print("- Aucune donnée trouvée pour la table Materiau, création d'un fichier vide")
	
	# Créer le fichier dans tous les cas
	print("Contenu CSV Materiau à écrire:")
	print(materiau_csv)
	
	var materiau_file = FileAccess.open("res://csv/export_materiau.csv", FileAccess.WRITE)
	if materiau_file:
		materiau_file.store_string(materiau_csv)
		materiau_file.close()
		print("✓ Table Materiau exportée vers : res://csv/export_materiau.csv")
	else:
		var error = FileAccess.get_open_error()
		print("✗ Erreur lors de l'export de la table Materiau, code erreur: ", error)
	
	# Export de la table Transforme
	print("Export de la table Transforme...")
	var transforme_result = db.select_rows("Transforme", "", ["*"])
	print("Résultat select_rows Transforme: ", transforme_result)
	print("Type de résultat Transforme: ", typeof(transforme_result))
	
	var transforme_csv = "ID,POSITION_X,POSITION_Y,POSITION_Z,ROTATION_X,ROTATION_Y,ROTATION_Z,SCALE_X,SCALE_Y,SCALE_Z\n"
	
	if transforme_result is Array and transforme_result.size() > 0:
		for row in transforme_result:
			transforme_csv += str(row["id"]) + "," + str(row["position_x"]) + "," + str(row["position_y"]) + "," + str(row["position_z"]) + ","
			transforme_csv += str(row["rotation_x"]) + "," + str(row["rotation_y"]) + "," + str(row["rotation_z"]) + ","
			transforme_csv += str(row["scale_x"]) + "," + str(row["scale_y"]) + "," + str(row["scale_z"]) + "\n"
		print("✓ ", transforme_result.size(), " transformations trouvées")
	else:
		print("- Aucune donnée trouvée pour la table Transforme, création d'un fichier vide")
	
	print("Contenu CSV Transforme à écrire:")
	print(transforme_csv)
	
	var transforme_file = FileAccess.open("res://csv/export_transforme.csv", FileAccess.WRITE)
	if transforme_file:
		transforme_file.store_string(transforme_csv)
		transforme_file.close()
		print("✓ Table Transforme exportée vers : res://csv/export_transforme.csv")
	else:
		print("✗ Erreur lors de l'export de la table Transforme")
	
	# Export de la table Objet
	print("Export de la table Objet...")
	var objet_result = db.select_rows("Objet", "", ["*"])
	print("Résultat select_rows Objet: ", objet_result)
	print("Type de résultat Objet: ", typeof(objet_result))
	
	var objet_csv = "ID,NOM,TRANSFORME_ID,MATERIAU_ID,SUR_ID\n"
	
	if objet_result is Array and objet_result.size() > 0:
		for row in objet_result:
			var sur_id_value = str(row.get("sur_id", "")) if row.has("sur_id") and row["sur_id"] != null else ""
			objet_csv += str(row["id"]) + "," + str(row["nom"]) + "," + str(row["transforme_id"]) + "," + str(row["materiau_id"]) + "," + sur_id_value + "\n"
		print("✓ ", objet_result.size(), " objets trouvés")
	else:
		print("- Aucune donnée trouvée pour la table Objet, création d'un fichier vide")
	
	print("Contenu CSV Objet à écrire:")
	print(objet_csv)
	
	var objet_file = FileAccess.open("res://csv/export_objet.csv", FileAccess.WRITE)
	if objet_file:
		objet_file.store_string(objet_csv)
		objet_file.close()
		print("✓ Table Objet exportée vers : res://csv/export_objet.csv")
	else:
		print("✗ Erreur lors de l'export de la table Objet")
	
	# Export de la table Sur
	print("Export de la table Sur...")
	var sur_result = db.select_rows("Sur", "", ["*"])
	print("Résultat select_rows Sur: ", sur_result)
	print("Type de résultat Sur: ", typeof(sur_result))
	
	var sur_csv = "ID,OBJET_ID,TEXTE\n"
	
	if sur_result is Array and sur_result.size() > 0:
		for row in sur_result:
			sur_csv += str(row["id"]) + "," + str(row["objet_id"]) + "," + str(row["texte"]) + "\n"
		print("✓ ", sur_result.size(), " données Sur trouvées")
	else:
		print("- Aucune donnée trouvée pour la table Sur, création d'un fichier vide")
	
	print("Contenu CSV Sur à écrire:")
	print(sur_csv)
	
	var sur_file = FileAccess.open("res://csv/export_sur.csv", FileAccess.WRITE)
	if sur_file:
		sur_file.store_string(sur_csv)
		sur_file.close()
		print("✓ Table Sur exportée vers : res://csv/export_sur.csv")
	else:
		print("✗ Erreur lors de l'export de la table Sur")
	
	# Export d'une vue combinée (reconstruction manuelle des JOIN)
	print("Export de la vue combinée...")
	
	# Récupérer toutes les données nécessaires séparément
	var objets_data = db.select_rows("Objet", "", ["*"])
	var transform_data = db.select_rows("Transforme", "", ["*"])
	var materiau_data = db.select_rows("Materiau", "", ["*"])
	var sur_data = db.select_rows("Sur", "", ["*"])
	
	print("Objets trouvés: ", objets_data.size() if objets_data is Array else 0)
	print("Transformations trouvées: ", transform_data.size() if transform_data is Array else 0)
	print("Matériaux trouvés: ", materiau_data.size() if materiau_data is Array else 0)
	print("Données Sur trouvées: ", sur_data.size() if sur_data is Array else 0)
	
	var combined_csv = "OBJET_ID,OBJET_NOM,POS_X,POS_Y,POS_Z,ROT_X,ROT_Y,ROT_Z,SCL_X,SCL_Y,SCL_Z,MATERIAU_NOM,POIDS,OPACITE,COULEUR,SUR_ID,SUR_TEXTE\n"
	
	if objets_data is Array and objets_data.size() > 0 and transform_data is Array and materiau_data is Array:
		for objet in objets_data:
			# Trouver la transformation correspondante
			var transform = null
			for t in transform_data:
				if t["id"] == objet["transforme_id"]:
					transform = t
					break
			
			# Trouver le matériau correspondant
			var materiau = null
			for m in materiau_data:
				if m["id"] == objet["materiau_id"]:
					materiau = m
					break
			
			# Trouver les données Sur correspondantes (si sur_id existe)
			var sur = null
			if objet.has("sur_id") and objet["sur_id"] != null and sur_data is Array:
				for s in sur_data:
					if s["id"] == objet["sur_id"]:
						sur = s
						break
			
			if transform != null and materiau != null:
				combined_csv += str(objet["id"]) + "," + str(objet["nom"]) + ","
				combined_csv += str(transform["position_x"]) + "," + str(transform["position_y"]) + "," + str(transform["position_z"]) + ","
				combined_csv += str(transform["rotation_x"]) + "," + str(transform["rotation_y"]) + "," + str(transform["rotation_z"]) + ","
				combined_csv += str(transform["scale_x"]) + "," + str(transform["scale_y"]) + "," + str(transform["scale_z"]) + ","
				combined_csv += str(materiau["nom"]) + "," + str(materiau["poids"]) + "," + str(materiau["opacite"]) + "," + str(materiau["couleur"]) + ","
				
				# Ajouter les données Sur
				if sur != null:
					combined_csv += str(sur["id"]) + "," + str(sur["texte"]) + "\n"
				else:
					combined_csv += "," + "\n"  # Champs vides si pas de données Sur
		
		print("✓ Vue combinée construite avec succès")
	else:
		print("- Aucune donnée trouvée pour la vue complète, création d'un fichier vide")
	
	print("Contenu CSV vue complète à écrire:")
	print(combined_csv)
	
	var combined_file = FileAccess.open("res://csv/export_vue_complete.csv", FileAccess.WRITE)
	if combined_file:
		combined_file.store_string(combined_csv)
		combined_file.close()
		print("✓ Vue complète exportée vers : res://csv/export_vue_complete.csv")
	else:
		print("✗ Erreur lors de l'export de la vue complète")
	
	print("================== EXPORT CSV TERMINÉ ==================")
	print("Fichiers générés dans le dossier CSV :")
	print("- csv/export_materiau.csv")
	print("- csv/export_transforme.csv") 
	print("- csv/export_objet.csv")
	print("- csv/export_sur.csv")
	print("- csv/export_vue_complete.csv")

func create_sample_data():
	print("=== CRÉATION DE DONNÉES D'EXEMPLE ===")
	
	# Créer quelques matériaux d'exemple
	create_default_materials()
	
	# Ajouter quelques transformations d'exemple
	print("Ajout de transformations d'exemple...")
	var transform1_result = db.query("INSERT INTO Transforme (position_x, position_y, position_z, rotation_x, rotation_y, rotation_z, scale_x, scale_y, scale_z) VALUES (0, 0, 0, 0, 0, 0, 1, 1, 1)")
	var transform2_result = db.query("INSERT INTO Transforme (position_x, position_y, position_z, rotation_x, rotation_y, rotation_z, scale_x, scale_y, scale_z) VALUES (5, 2, -3, 0, 45, 0, 2, 2, 2)")
	var transform3_result = db.query("INSERT INTO Transforme (position_x, position_y, position_z, rotation_x, rotation_y, rotation_z, scale_x, scale_y, scale_z) VALUES (-2, 3, 1, 15, 0, 30, 0.5, 0.5, 0.5)")
	print("Transform insertions: ", transform1_result, ", ", transform2_result, ", ", transform3_result)
	
	# Ajouter quelques données Sur d'exemple d'abord
	print("Ajout de données Sur d'exemple...")
	save_sur(1, "Objet en bois très résistant")
	save_sur(2, "Pierre sculptée avec des motifs anciens")
	save_sur(3, "Cylindre métallique avec surface polie")
	save_sur(1, "Texture rugueuse visible sur les côtés")
	
	# Ajouter quelques objets d'exemple (certains avec des liens vers Sur)
	print("Ajout d'objets d'exemple...")
	var objet1_result = db.query("INSERT INTO Objet (nom, transforme_id, materiau_id, sur_id) VALUES ('CubeBois', 1, 1, 1)")
	var objet2_result = db.query("INSERT INTO Objet (nom, transforme_id, materiau_id, sur_id) VALUES ('SpherePierre', 2, 2, 2)")
	var objet3_result = db.query("INSERT INTO Objet (nom, transforme_id, materiau_id) VALUES ('CylindreMetal', 3, 3)")
	print("Object insertions: ", objet1_result, ", ", objet2_result, ", ", objet3_result)
	
	print("✓ Données d'exemple créées")

func clear_all_data():
	print("=== SUPPRESSION DE TOUTES LES DONNÉES ===")
	db.query("DELETE FROM Sur")
	db.query("DELETE FROM Objet")
	db.query("DELETE FROM Transforme") 
	db.query("DELETE FROM Materiau")
	print("✓ Toutes les données supprimées")

func _exit_tree():
	if db:
		db.close_db()
