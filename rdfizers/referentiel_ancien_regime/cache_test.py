from sherlockcachemanagement import Cache
import yaml

# CACHE

mon_cache = Cache("test.yaml")

mon_cache.get_uuid(["tesœt"], True)

with open("test.yaml", "r", encoding="utf-8") as file:
	file_parse = yaml.load(file, Loader=yaml.FullLoader)
	for cle in file_parse.keys():
		print(cle)

mon_cache.bye()