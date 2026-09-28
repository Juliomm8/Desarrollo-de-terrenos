using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.Collections.Generic;

public class AlienForestGenerator : EditorWindow
{
    [MenuItem("Tools/Generar Bosque Alienígena")]
    public static void GenerateForest()
    {
        // 1. Carga de Prefabs
        List<GameObject> treePrefabs = new List<GameObject>();
        for (int i = 1; i <= 12; i++)
        {
            string path = $"Assets/Cartoon low poly tree/Prefabs/tree{i:D2}.prefab";
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab != null)
            {
                treePrefabs.Add(prefab);
            }
            else
            {
                Debug.LogWarning($"No se pudo encontrar el prefab: {path}");
            }
        }

        if (treePrefabs.Count == 0)
        {
            Debug.LogError("No se encontraron prefabs de árboles en la ruta especificada.");
            return;
        }

        // 2. Límites del Mapa
        Terrain terrain = Terrain.activeTerrain;
        if (terrain == null)
        {
            Debug.LogError("No hay un terreno activo en la escena.");
            return;
        }

        TerrainData terrainData = terrain.terrainData;
        Vector3 terrainPos = terrain.transform.position;
        Vector3 terrainSize = terrainData.size;

        Vector3 mapCenter = terrainPos + new Vector3(terrainSize.x / 2f, 0, terrainSize.z / 2f);
        float exclusionRadius = 50f;
        int treesToSpawn = 150;
        int treesSpawned = 0;
        int maxAttempts = 10000;
        int attempts = 0;

        // 8. Organización
        GameObject forestParent = new GameObject("Bosque_Alienigena");

        while (treesSpawned < treesToSpawn && attempts < maxAttempts)
        {
            attempts++;

            // 4. Posicionamiento
            float randomX = Random.Range(terrainPos.x, terrainPos.x + terrainSize.x);
            float randomZ = Random.Range(terrainPos.z, terrainPos.z + terrainSize.z);

            // 5. Zona de Exclusión (Cosmic Diner)
            Vector2 treePos2D = new Vector2(randomX, randomZ);
            Vector2 centerPos2D = new Vector2(mapCenter.x, mapCenter.z);
            if (Vector2.Distance(treePos2D, centerPos2D) < exclusionRadius)
            {
                continue; // Ignorar y calcular otra nueva
            }

            // 7. Anclaje Topográfico
            float yPos = terrain.SampleHeight(new Vector3(randomX, 0, randomZ)) + terrainPos.y;
            Vector3 finalPosition = new Vector3(randomX, yPos, randomZ);

            // 3. Generación Aleatoria
            GameObject selectedPrefab = treePrefabs[Random.Range(0, treePrefabs.Count)];
            GameObject newTree = (GameObject)PrefabUtility.InstantiatePrefab(selectedPrefab);
            
            newTree.transform.position = finalPosition;
            newTree.transform.SetParent(forestParent.transform);

            // 6. Adaptación Orgánica
            float randomScale = Random.Range(0.8f, 2.5f);
            newTree.transform.localScale = new Vector3(randomScale, randomScale, randomScale);
            newTree.transform.rotation = Quaternion.Euler(0, Random.Range(0f, 360f), 0);

            treesSpawned++;
        }

        if (treesSpawned < treesToSpawn)
        {
            Debug.LogWarning($"Solo se pudieron generar {treesSpawned} árboles de {treesToSpawn}.");
        }
        else
        {
            Debug.Log("¡Bosque alienígena generado con éxito!");
        }

        // Guardar la escena
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
    }
}
