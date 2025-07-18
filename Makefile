

install:
	pip install -r requirements.txt


del_institution:
	python3 delete_institution.py $(ID)

del_collection:
	python3 delete_collection.py $(ID)


del_group:
	python3 delete_group.py $(ID)


del_record:
	python3 delete_record.py $(ID)