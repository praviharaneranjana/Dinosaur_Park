using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using MiniGame.Interactions;

namespace MiniGame.Editor
{
    public static class ModernParkMapAssembler
    {
        private const string ScenePath = "Assets/Scenes/DinosaurPark.unity";
        private const string MaterialsDir = "Assets/Materials/EcoPark";

        [MenuItem("Tools/MiniGame/Assemble Complete Modern Dinosaur Park")]
        [InitializeOnLoadMethod]
        public static void InitializeHook()
        {
            EditorApplication.delayCall += () =>
            {
                if (SceneManager.GetActiveScene().name == "DinosaurPark")
                {
                    if (GameObject.Find("=== Modern Eco Dinosaur Park ===") == null)
                    {
                        AssembleModernPark();
                    }
                }
            };
        }

        public static void AssembleModernPark()
        {
            Debug.Log("[ModernParkMapAssembler] Assembling detailed modern park map matching ParkMap_Overview.png...");

            Scene activeScene = SceneManager.GetActiveScene();
            if (activeScene.path != ScenePath)
            {
                if (File.Exists(ScenePath))
                {
                    activeScene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
                }
            }

            if (!AssetDatabase.IsValidFolder("Assets/Materials"))
                AssetDatabase.CreateFolder("Assets", "Materials");
            if (!AssetDatabase.IsValidFolder(MaterialsDir))
                AssetDatabase.CreateFolder("Assets/Materials", "EcoPark");

            Shader urpLit = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");

            // Setup Eco-Park Palette Materials matching high-detail 3D geometry
            Material matConcrete = GetOrCreateMat("M_Eco_Concrete", new Color(0.957f, 0.929f, 0.847f), 0.18f, 0.0f, urpLit);
            Material matTimber = GetOrCreateMat("M_Eco_Timber", new Color(0.780f, 0.604f, 0.388f), 0.45f, 0.0f, urpLit);
            Material matSteel = GetOrCreateMat("M_Eco_CharcoalSteel", new Color(0.231f, 0.278f, 0.263f), 0.3f, 0.88f, urpLit);
            Material matGlass = GetOrCreateMat("M_Eco_TealGlass", new Color(0.561f, 0.796f, 0.796f, 0.85f), 0.12f, 0.2f, urpLit);
            Material matLivingRoof = GetOrCreateMat("M_Eco_LivingRoof", new Color(0.369f, 0.608f, 0.290f), 0.9f, 0.0f, urpLit);
            Material matBrass = GetOrCreateMat("M_Eco_BrassGold", new Color(0.949f, 0.722f, 0.294f), 0.22f, 0.92f, urpLit, true, new Color(0.949f, 0.722f, 0.294f) * 1.6f);
            Material matAmber = GetOrCreateMat("M_Eco_AmberGlow", new Color(1.0f, 0.65f, 0.18f), 0.2f, 0.1f, urpLit, true, new Color(1.0f, 0.65f, 0.18f) * 3.2f);
            Material matSolar = GetOrCreateMat("M_Eco_SolarPanel", new Color(0.10f, 0.16f, 0.26f), 0.18f, 0.6f, urpLit);
            Material matRoad = GetOrCreateMat("M_Eco_RoadAsphalt", new Color(0.18f, 0.19f, 0.20f), 0.12f, 0.0f, urpLit);
            Material matYellow = GetOrCreateMat("M_Eco_RoadYellow", new Color(0.92f, 0.75f, 0.15f), 0.4f, 0.0f, urpLit);
            Material matWhite = GetOrCreateMat("M_Eco_RoadWhite", new Color(0.90f, 0.90f, 0.88f), 0.4f, 0.0f, urpLit);
            Material matSoil = GetOrCreateMat("M_Eco_Soil", new Color(0.24f, 0.19f, 0.14f), 0.95f, 0.0f, urpLit);
            Material matFoliage = GetOrCreateMat("M_Eco_Foliage", new Color(0.28f, 0.52f, 0.22f), 0.8f, 0.0f, urpLit);
            Material matHvac = GetOrCreateMat("M_Eco_HVAC", new Color(0.45f, 0.47f, 0.48f), 0.45f, 0.5f, urpLit);
            Material matParasol = GetOrCreateMat("M_Eco_Parasol", new Color(0.92f, 0.88f, 0.78f), 0.75f, 0.0f, urpLit);
            Material matBinGreen = GetOrCreateMat("M_Eco_BinGreen", new Color(0.22f, 0.68f, 0.32f), 0.3f, 0.0f, urpLit);
            Material matBinTeal = GetOrCreateMat("M_Eco_BinTeal", new Color(0.22f, 0.72f, 0.72f), 0.3f, 0.0f, urpLit);
            Material matBinGold = GetOrCreateMat("M_Eco_BinGold", new Color(0.92f, 0.72f, 0.18f), 0.3f, 0.0f, urpLit);

            Dictionary<string, Material> materialLookup = new Dictionary<string, Material>
            {
                { "Mat_Concrete", matConcrete },
                { "Mat_Timber", matTimber },
                { "Mat_CharcoalSteel", matSteel },
                { "Mat_TealGlass", matGlass },
                { "Mat_LivingRoof", matLivingRoof },
                { "Mat_BrassGold", matBrass },
                { "Mat_AmberGlow", matAmber },
                { "Mat_SolarPanel", matSolar },
                { "Mat_RoadAsphalt", matRoad },
                { "Mat_RoadYellow", matYellow },
                { "Mat_RoadWhite", matWhite },
                { "Mat_RoadMarking", matWhite },
                { "Mat_SoilDark", matSoil },
                { "Mat_FoliageBush", matFoliage },
                { "Mat_HVAC_Grey", matHvac },
                { "Mat_ParasolFabric", matParasol },
                { "Mat_Bin_Green", matBinGreen },
                { "Mat_Bin_Teal", matBinTeal },
                { "Mat_Bin_Gold", matBinGold }
            };

            // Remove previous modern park parent if re-running
            GameObject oldPark = GameObject.Find("=== Modern Eco Dinosaur Park ===");
            if (oldPark != null) Object.DestroyImmediate(oldPark);

            // Master Parent Category
            GameObject modernParkRoot = new GameObject("=== Modern Eco Dinosaur Park ===");

            Transform catAvenue = CreateCategory("=== Park Entrance Avenue ===", modernParkRoot.transform);
            Transform catRoads = CreateCategory("=== Central Road & Walkway Network ===", modernParkRoot.transform);
            Transform catVisitorHub = CreateCategory("=== Visitor Hub: Dining & Science ===", modernParkRoot.transform);
            Transform catEnclosure = CreateCategory("=== Enclosure Security & Viewing ===", modernParkRoot.transform);
            Transform catFurniture = CreateCategory("=== Park Street Furniture & Props ===", modernParkRoot.transform);
            Transform catCharacters = CreateCategory("=== Park Visitors & Guests ===", modernParkRoot.transform);

            // 1. Grand Entrance Gate Building (Z = -45.0m)
            GameObject entranceGate = InstantiateModel("Assets/Models/Buildings/EntranceGate.fbx", new Vector3(0, 0, -45.0f), Quaternion.identity, catAvenue, materialLookup);
            if (entranceGate != null)
            {
                entranceGate.name = "Modern Entrance Gate & Ticket Pavilion";
                AddMeshColliders(entranceGate);

                Transform ticketDoor = entranceGate.transform.Find("Door_TicketPavilion");
                if (ticketDoor != null)
                {
                    InteractiveDoor doorScript = entranceGate.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.HingeSwing);
                    SetPrivateField(doorScript, "primaryDoorLeaf", ticketDoor);
                    SetPrivateField(doorScript, "swingAngle", 85f);
                    SetPrivateField(doorScript, "sensorRadius", 3.0f);
                }
            }

            // 2. Central Road Network with Yellow Divider Lines & Crosswalks
            // Incoming Road South of Gate
            for (float z = -57.0f; z <= -49.0f; z += 4.0f)
            {
                InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(0, 0, z), Quaternion.identity, catRoads, materialLookup);
            }

            // Main Avenue Road North of Gate up to Crossroads
            for (float z = -41.0f; z <= -26.0f; z += 4.0f)
            {
                InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(0, 0, z), Quaternion.identity, catRoads, materialLookup);
            }

            // 4-Way Crossroad Intersection at (0, 0, -22) with Zebra Crosswalks
            InstantiateModel("Assets/Models/Roads/ModularRoad_Cross.fbx", new Vector3(0, 0, -22.0f), Quaternion.identity, catRoads, materialLookup);

            // East Road Branch (to Research Lab & Hatchery)
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(4.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(8.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(12.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Corner.fbx", new Vector3(16.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(16.0f, 0, -26.0f), Quaternion.identity, catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_End.fbx", new Vector3(16.0f, 0, -30.0f), Quaternion.Euler(0, 180f, 0), catRoads, materialLookup);

            // Marked Parking Bays in front of Research Lab
            InstantiateModel("Assets/Models/Roads/ModularRoad_Parking.fbx", new Vector3(10.0f, 0, -18.0f), Quaternion.Euler(0, 180f, 0), catRoads, materialLookup);

            // West Road Branch (to Canteen Dining Terrace)
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(-4.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(-8.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(-12.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            InstantiateModel("Assets/Models/Roads/ModularRoad_End.fbx", new Vector3(-16.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);

            // North Road continuing straight to Enclosure Security Gate
            for (float z = -18.0f; z <= -4.0f; z += 4.0f)
            {
                InstantiateModel("Assets/Models/Roads/ModularRoad_Straight.fbx", new Vector3(0, 0, z), Quaternion.identity, catRoads, materialLookup);
            }

            // Pedestrian Walkway Pavers
            for (float x = -13.0f; x >= -17.0f; x -= 2.0f)
            {
                InstantiateModel("Assets/Models/Roads/PedestrianPath_Straight.fbx", new Vector3(x, 0, -18.0f), Quaternion.Euler(0, 90f, 0), catRoads, materialLookup);
            }
            for (float z = -20.0f; z <= -16.0f; z += 2.0f)
            {
                InstantiateModel("Assets/Models/Roads/PedestrianPath_Straight.fbx", new Vector3(14.0f, 0, z), Quaternion.identity, catRoads, materialLookup);
            }

            // 3. Visitor Hub: High-Detail Canteen & Dining Terrace (X = -20m, Z = -22m)
            GameObject canteen = InstantiateModel("Assets/Models/Buildings/Canteen.fbx", new Vector3(-20.0f, 0, -22.0f), Quaternion.Euler(0, 90f, 0), catVisitorHub, materialLookup);
            if (canteen != null)
            {
                canteen.name = "Park Canteen & Terrace Cafe";
                AddMeshColliders(canteen);

                Transform staffDoor = canteen.transform.Find("Canteen_StaffDoor");
                if (staffDoor != null)
                {
                    InteractiveDoor doorScript = canteen.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.HingeSwing);
                    SetPrivateField(doorScript, "primaryDoorLeaf", staffDoor);
                    SetPrivateField(doorScript, "swingAngle", 90f);
                    SetPrivateField(doorScript, "sensorRadius", 3.0f);
                }
            }

            // 4. Visitor Hub: High-Detail Research Lab (X = 18m, Z = -14m)
            GameObject researchLab = InstantiateModel("Assets/Models/Buildings/ResearchLab.fbx", new Vector3(18.0f, 0, -14.0f), Quaternion.Euler(0, 180f, 0), catVisitorHub, materialLookup);
            if (researchLab != null)
            {
                researchLab.name = "Dinosaur Genomics Research Lab";
                AddMeshColliders(researchLab);

                Transform doorL = researchLab.transform.Find("ResearchLab_Door_L");
                Transform doorR = researchLab.transform.Find("ResearchLab_Door_R");
                if (doorL != null && doorR != null)
                {
                    InteractiveDoor doorScript = researchLab.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.DoubleSlide);
                    SetPrivateField(doorScript, "primaryDoorLeaf", doorL);
                    SetPrivateField(doorScript, "secondaryDoorLeaf", doorR);
                    SetPrivateField(doorScript, "slideDistance", 0.95f);
                    SetPrivateField(doorScript, "sensorRadius", 4.5f);
                }
            }

            // 5. Visitor Hub: High-Detail Hatchery Dome (X = 22m, Z = -32m)
            GameObject hatchery = InstantiateModel("Assets/Models/Buildings/Hatchery.fbx", new Vector3(22.0f, 0, -32.0f), Quaternion.Euler(0, -90f, 0), catVisitorHub, materialLookup);
            if (hatchery != null)
            {
                hatchery.name = "Dinosaur Embryo Hatchery";
                AddMeshColliders(hatchery);

                Transform doorL = hatchery.transform.Find("Hatchery_Door_L");
                Transform doorR = hatchery.transform.Find("Hatchery_Door_R");
                if (doorL != null && doorR != null)
                {
                    InteractiveDoor doorScript = hatchery.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.DoubleSlide);
                    SetPrivateField(doorScript, "primaryDoorLeaf", doorL);
                    SetPrivateField(doorScript, "secondaryDoorLeaf", doorR);
                    SetPrivateField(doorScript, "slideDistance", 1.35f);
                    SetPrivateField(doorScript, "sensorRadius", 5.0f);
                }
            }

            // 6. High-Rise Ranger Station & Lookout Tower (X = -18m, Z = -5m)
            GameObject rangerStation = InstantiateModel("Assets/Models/Buildings/RangerStation.fbx", new Vector3(-18.0f, 0, -5.0f), Quaternion.identity, catVisitorHub, materialLookup);
            if (rangerStation != null)
            {
                rangerStation.name = "Park Ranger Headquarters & Watchtower";
                AddMeshColliders(rangerStation);

                Transform door = rangerStation.transform.Find("RangerStation_Door");
                if (door != null)
                {
                    InteractiveDoor doorScript = rangerStation.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.HingeSwing);
                    SetPrivateField(doorScript, "primaryDoorLeaf", door);
                    SetPrivateField(doorScript, "swingAngle", 90f);
                    SetPrivateField(doorScript, "sensorRadius", 3.0f);
                }
            }

            // 7. Enclosure Security & Viewing (Automatic Security Gate at Z = 0)
            GameObject autoGate = InstantiateModel("Assets/Models/Enclosures/AutomaticGate.fbx", new Vector3(0, 0, 0), Quaternion.identity, catEnclosure, materialLookup);
            if (autoGate != null)
            {
                autoGate.name = "Automatic Perimeter Security Gate";
                AddMeshColliders(autoGate);

                Transform gateL = autoGate.transform.Find("AutoGate_Door_L");
                Transform gateR = autoGate.transform.Find("AutoGate_Door_R");
                if (gateL != null && gateR != null)
                {
                    InteractiveDoor doorScript = autoGate.AddComponent<InteractiveDoor>();
                    SetPrivateField(doorScript, "motionType", DoorMotionType.DoubleSlide);
                    SetPrivateField(doorScript, "primaryDoorLeaf", gateL);
                    SetPrivateField(doorScript, "secondaryDoorLeaf", gateR);
                    SetPrivateField(doorScript, "slideDistance", 1.7f);
                    SetPrivateField(doorScript, "sensorRadius", 6.5f);
                    SetPrivateField(doorScript, "transitionDuration", 1.6f);

                    Transform beaconL = autoGate.transform.Find("Pylon_L/Beacon_Light_L");
                    if (beaconL != null && beaconL.TryGetComponent<Renderer>(out var rend))
                    {
                        SetPrivateField(doorScript, "statusBeaconRenderer", rend);
                    }
                }
            }

            // Panoramic Viewing Walls along perimeter fence (X = -8m, -10m, and +8m, +10m)
            InstantiateModel("Assets/Models/Enclosures/ViewingWall.fbx", new Vector3(-8.0f, 0, 0), Quaternion.identity, catEnclosure, materialLookup);
            InstantiateModel("Assets/Models/Enclosures/ViewingWall.fbx", new Vector3(-10.0f, 0, 0), Quaternion.identity, catEnclosure, materialLookup);
            InstantiateModel("Assets/Models/Enclosures/ViewingWall.fbx", new Vector3(8.0f, 0, 0), Quaternion.identity, catEnclosure, materialLookup);
            InstantiateModel("Assets/Models/Enclosures/ViewingWall.fbx", new Vector3(10.0f, 0, 0), Quaternion.identity, catEnclosure, materialLookup);

            // High-Detail Automated Feeder inside paddock (X = 12m, Z = 20m)
            GameObject feeder = InstantiateModel("Assets/Models/Enclosures/AutomatedFeeder.fbx", new Vector3(12.0f, 0, 20.0f), Quaternion.Euler(0, -45f, 0), catEnclosure, materialLookup);
            if (feeder != null)
            {
                feeder.name = "Paddock Automated Feeder Alpha";
                AddMeshColliders(feeder);
            }

            // 8. Street Furniture & Lighting Props
            // Modern Lamp Posts along Avenue
            for (float z = -40.0f; z <= -6.0f; z += 12.0f)
            {
                InstantiateModel("Assets/Models/Props/ModernLampPost.fbx", new Vector3(-2.8f, 0, z), Quaternion.Euler(0, 90f, 0), catFurniture, materialLookup);
                InstantiateModel("Assets/Models/Props/ModernLampPost.fbx", new Vector3(2.8f, 0, z), Quaternion.Euler(0, -90f, 0), catFurniture, materialLookup);
            }

            // Benches, Recycling Bins, and Planters
            InstantiateModel("Assets/Models/Props/ParkBench.fbx", new Vector3(-14.0f, 0, -20.0f), Quaternion.Euler(0, 90f, 0), catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/ParkBench.fbx", new Vector3(-14.0f, 0, -24.0f), Quaternion.Euler(0, 90f, 0), catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/ParkBench.fbx", new Vector3(13.0f, 0, -24.0f), Quaternion.Euler(0, -90f, 0), catFurniture, materialLookup);

            InstantiateModel("Assets/Models/Props/RecyclingBin.fbx", new Vector3(-2.6f, 0, -20.0f), Quaternion.Euler(0, 90f, 0), catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/RecyclingBin.fbx", new Vector3(2.6f, 0, -20.0f), Quaternion.Euler(0, -90f, 0), catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/RecyclingBin.fbx", new Vector3(-2.6f, 0, -42.0f), Quaternion.Euler(0, 90f, 0), catFurniture, materialLookup);

            InstantiateModel("Assets/Models/Props/Planter.fbx", new Vector3(-3.2f, 0, -43.0f), Quaternion.identity, catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/Planter.fbx", new Vector3(3.2f, 0, -43.0f), Quaternion.identity, catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/Planter.fbx", new Vector3(-2.8f, 0, -2.5f), Quaternion.identity, catFurniture, materialLookup);
            InstantiateModel("Assets/Models/Props/Planter.fbx", new Vector3(2.8f, 0, -2.5f), Quaternion.identity, catFurniture, materialLookup);

            // 9. Natural Trees & Vegetation Framing (Pine & Common Trees from library)
            for (float pz = -52.0f; pz <= -35.0f; pz += 6.0f)
            {
                InstantiateEnvModel("Assets/Models/Environment/Models/Pine_1.fbx", new Vector3(-7.5f, 0, pz), Quaternion.Euler(0, Random.Range(0, 360), 0), catFurniture);
                InstantiateEnvModel("Assets/Models/Environment/Models/Pine_2.fbx", new Vector3(7.5f, 0, pz), Quaternion.Euler(0, Random.Range(0, 360), 0), catFurniture);
            }

            // 10. Park Visitors & Characters
            InstantiateEnvModel("Assets/Models/Characters/Male/Poses/Male_Sitting.fbx", new Vector3(-20.0f, 0.45f, -24.2f), Quaternion.Euler(0, 45f, 0), catCharacters);
            InstantiateEnvModel("Assets/Models/Characters/Male/Poses/Male_Sitting_Cheering.fbx", new Vector3(-20.0f, 0.45f, -22.2f), Quaternion.Euler(0, -45f, 0), catCharacters);
            InstantiateEnvModel("Assets/Models/Characters/Male/Poses/Male_Standing_Waving.fbx", new Vector3(-3.5f, 0, -40.0f), Quaternion.Euler(0, 60f, 0), catCharacters);
            InstantiateEnvModel("Assets/Models/Characters/Male/Poses/Male_Walking.fbx", new Vector3(1.2f, 0, -20.0f), Quaternion.Euler(0, 0f, 0), catCharacters);
            InstantiateEnvModel("Assets/Models/Characters/Male/Poses/Male_LookingUp.fbx", new Vector3(-8.5f, 0, -1.5f), Quaternion.Euler(0, 0f, 0), catCharacters);

            EditorSceneManager.MarkSceneDirty(activeScene);
            EditorSceneManager.SaveScene(activeScene);

            Debug.Log("[ModernParkMapAssembler] Modern Dinosaur Eco-Park map fully updated and saved successfully!");
        }

        private static Transform CreateCategory(string name, Transform parent)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent);
            return go.transform;
        }

        private static GameObject InstantiateModel(string path, Vector3 position, Quaternion rotation, Transform parent, Dictionary<string, Material> materials)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null)
            {
                Debug.LogWarning($"[ModernParkMapAssembler] Could not load model at: {path}");
                return null;
            }

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            instance.transform.SetParent(parent);
            instance.transform.position = position;
            instance.transform.rotation = rotation;

            foreach (var renderer in instance.GetComponentsInChildren<MeshRenderer>(true))
            {
                var sharedMats = renderer.sharedMaterials;
                for (int i = 0; i < sharedMats.Length; i++)
                {
                    if (sharedMats[i] != null && materials.TryGetValue(sharedMats[i].name, out var replacement))
                    {
                        sharedMats[i] = replacement;
                    }
                }
                renderer.sharedMaterials = sharedMats;
            }

            return instance;
        }

        private static GameObject InstantiateEnvModel(string path, Vector3 position, Quaternion rotation, Transform parent)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) return null;

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            instance.transform.SetParent(parent);
            instance.transform.position = position;
            instance.transform.rotation = rotation;
            return instance;
        }

        private static void AddMeshColliders(GameObject root)
        {
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh != null && mf.GetComponent<Collider>() == null)
                {
                    if (!mf.name.Contains("Door") && !mf.name.Contains("Gate_L") && !mf.name.Contains("Gate_R"))
                    {
                        var col = mf.gameObject.AddComponent<MeshCollider>();
                        col.convex = false;
                    }
                    else
                    {
                        mf.gameObject.AddComponent<BoxCollider>();
                    }
                }
            }
        }

        private static Material GetOrCreateMat(string name, Color baseColor, float roughness, float metallic, Shader shader, bool isEmissive = false, Color? emissiveColor = null)
        {
            string path = $"{MaterialsDir}/{name}.mat";
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }

            mat.color = baseColor;
            if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", baseColor);
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", 1.0f - roughness);
            if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);

            if (isEmissive && emissiveColor.HasValue)
            {
                mat.EnableKeyword("_EMISSION");
                if (mat.HasProperty("_EmissionColor")) mat.SetColor("_EmissionColor", emissiveColor.Value);
            }

            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static void SetPrivateField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public);
            if (field != null)
            {
                field.SetValue(target, value);
            }
        }
    }
}
