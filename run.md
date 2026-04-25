docker build -f pdf_extractor/docker/Dockerfile -t pdf-extractor .


docker run --rm -p 8080:8080 pdf-extractor