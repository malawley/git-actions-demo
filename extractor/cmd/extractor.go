package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"cloud.google.com/go/storage"
)

const apiURL = "https://data.cityofchicago.org/resource/4ijn-s7e5.json"

var bucketName = os.Getenv("RAW_BUCKET")

func main() {
	http.HandleFunc("/extract", handleExtract)
	http.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	log.Printf("🚀 Extractor running on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func handleExtract(w http.ResponseWriter, r *http.Request) {
	ctx := context.Background()

	nStr := r.URL.Query().Get("n")
	date := r.URL.Query().Get("date")
	if nStr == "" || date == "" {
		http.Error(w, "Missing 'n' or 'date' query parameters", http.StatusBadRequest)
		return
	}

	n, err := strconv.Atoi(nStr)
	if err != nil || n <= 0 {
		http.Error(w, "'n' must be a positive integer", http.StatusBadRequest)
		return
	}

	url := fmt.Sprintf("%s?$limit=%d", apiURL, n)
	resp, err := http.Get(url)
	if err != nil {
		http.Error(w, "API fetch failed: "+err.Error(), 500)
		return
	}
	defer resp.Body.Close()

	var data []map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		http.Error(w, "JSON decode error: "+err.Error(), 500)
		return
	}

	storageClient, err := storage.NewClient(ctx)
	if err != nil {
		http.Error(w, "GCS client error: "+err.Error(), 500)
		return
	}
	defer storageClient.Close()

	filename := fmt.Sprintf("git-action-demo/%s/food_inspections_raw.json", date)
	if err := writeToGCS(ctx, storageClient, bucketName, filename, data); err != nil {
		http.Error(w, "GCS write error: "+err.Error(), 500)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":   "success",
		"rows":     len(data),
		"filename": filename,
	})
}

func writeToGCS(ctx context.Context, client *storage.Client, bucket, filename string, data interface{}) error {
	obj := client.Bucket(bucket).Object(filename)
	writer := obj.NewWriter(ctx)
	defer writer.Close()
	enc := json.NewEncoder(writer)
	return enc.Encode(data)
}
