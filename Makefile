schemas/dotenv.schema.json: generators/dotenv.schema.jsonnet
	jsonnet $< | jq -S | tee $@

models/DotenvSchema.py: schemas/dotenv.schema.json
	datamodel-codegen --disable-timestamp --input-file-type jsonschema --input $< --output $@

docker-image:
	DOCKER_BUILDKIT=1 time docker build --progress=plain --ssh default -t cks_memorial_hall-chain-test -f Dockerfile.script .


