build:
	docker build . -t fb-photos:latest

run: build
	docker run \
		-e FACEBOOK_TOKEN=$(FACEBOOK_TOKEN) \
		-v $(PWD)/output:/output \
		fb-photos

download-chrome-driver:
	curl -O https://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip && \
	sudo unzip chromedriver_linux64.zip -d /usr/bin && \
	rm ./chromedriver_linux64.zip

download-firefox-driver:
	curl -O -L "https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz" && \
	tar -xvzf "geckodriver-v0.23.0-linux64.tar.gz" && \
	sudo mv geckodriver /usr/bin/geckodriver && \
	rm geckodriver-v0.23.0-linux64.tar.gz