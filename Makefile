build:
	docker build \
		--tag swag_proxy_confs_scanner:latest \
		.

run:
	docker run \
		--rm \
		-it \
		--name swag_proxy_confs_scanner \
		swag_proxy_confs_scanner:latest
