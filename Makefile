all: test

test:
	pip install pytest pytest-flakes pytest-pep8
	DJANGO_SETTINGS_MODULE=hydraclient.contrib.django.hydraclient.test_settings py.test --doctest-modules hydraclient --flakes --pep8

demo:
	WEATHER_BASE_URL=file://`pwd`/examples/services/weather/index.ttl PORT=8000 foreman start

docs: ./examples/service/weather/index.svg

clean:
	rm -f ./examples/service/weather/*.svg

./examples/service/weather/index.svg:
	rdfcat \
	    -n ./examples/services/weather/index.ttl \
	    > ./examples/services/weather/index.rdf

	java \
	    -jar ./bin/rdf2dot.jar  \
            -p "hydra" "http://www.w3.org/ns/hydra/core#" \
	    -p "weather" "http://vocab-ld.org/vocab/weather#" \
	    ./examples/services/weather/index.rdf \
	    > ./examples/services/weather/index-src.dot

	cat \
	    ./examples/services/weather/index-src.dot \
            | sed "s|digraph G|digraph Index|" \
            | sed "s|shape=box,|shape=circle,|" \
            | sed 's|shape="ellipse"|shape="rectangle"|' \
            | sed 's|color=gray|fillcolor=black,style=filled,fontcolor=white|' \
            | sed "s|file://`pwd`/examples/services/weather/|./|" \
            | sed 's|shape=circle,label="./index.ttl|shape=star,label="./index.ttl|' \
	    > ./examples/services/weather/index.dot

	dot \
            -Tsvg ./examples/services/weather/index.dot \
	    > ./examples/services/weather/index.svg
