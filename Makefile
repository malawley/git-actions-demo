# === CONFIGURATION ===
PROJECT_ID := hygiene-prediction-434
REGION := us-central1

# === EXTRACTOR ===
extractor-image := extractor-demo
extractor-service := extractor-git-action-demo
extractor-dir := extractor
RAW_BUCKET := raw-inspection-data-434

deploy-extractor:
	docker build -t $(extractor-image) $(extractor-dir)
	docker tag $(extractor-image) gcr.io/$(PROJECT_ID)/$(extractor-image)
	docker push gcr.io/$(PROJECT_ID)/$(extractor-image)
	gcloud run deploy $(extractor-service) \
		--image gcr.io/$(PROJECT_ID)/$(extractor-image) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--set-env-vars RAW_BUCKET=$(RAW_BUCKET)

# === STREAMLIT UI ===
app-image := streamlit-ui-demo
app-service := streamlit-ui-demo
app-dir := streamlit_ui
EXTRACTOR_URL := https://extractor-git-action-demo-931515156181.us-central1.run.app

deploy-app:
	docker build -t $(app-image) $(app-dir)
	docker tag $(app-image) gcr.io/$(PROJECT_ID)/$(app-image)
	docker push gcr.io/$(PROJECT_ID)/$(app-image)
	gcloud run deploy $(app-service) \
		--image gcr.io/$(PROJECT_ID)/$(app-image) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--set-env-vars EXTRACTOR_URL=$(EXTRACTOR_URL),RAW_BUCKET=$(RAW_BUCKET)
