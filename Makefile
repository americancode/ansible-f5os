PYTHON ?= python3
ANSIBLE_LOCAL_TEMP ?= .ansible/localtmp
ANSIBLE_REMOTE_TEMP ?= .ansible/tmp
ANSIBLE_COLLECTIONS_PATH ?= $(CURDIR)/.ansible/collections:/opt/ansible/collections
VALIDATION_IMAGE ?= ansible-f5os-validation:latest

.PHONY: validate validate-vars validate-ansible validate-image-build validate-image-run

validate: validate-vars validate-ansible

validate-vars:
	$(PYTHON) tools/validate-vars.py

validate-ansible:
	mkdir -p $(ANSIBLE_LOCAL_TEMP) $(ANSIBLE_REMOTE_TEMP)
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/bootstrap.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/system.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/network.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/qos.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/tenants.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/software_lifecycle.yml
	ANSIBLE_LOCAL_TEMP=$(ANSIBLE_LOCAL_TEMP) ANSIBLE_REMOTE_TEMP=$(ANSIBLE_REMOTE_TEMP) ANSIBLE_COLLECTIONS_PATH=$(ANSIBLE_COLLECTIONS_PATH) ansible-playbook --syntax-check playbooks/observability.yml

validate-image-build:
	docker build -f Dockerfile.validation -t $(VALIDATION_IMAGE) .

validate-image-run:
	docker run --rm -v "$$(pwd):/workspace" -w /workspace $(VALIDATION_IMAGE) make validate
