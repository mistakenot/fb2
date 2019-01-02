build:
	docker build . -t fb-photos:latest

run: build
	docker run \
		-e FACEBOOK_TOKEN=$(FACEBOOK_TOKEN) \
		-v $(PWD)/output:/output \
		fb-photos