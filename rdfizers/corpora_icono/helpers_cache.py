import argparse
from sherlockcachemanagement import Cache

# cache_images = None
# cache_corpus = None
# cache_personnes = None
# cache_lieux = None
# cache_vocab_estampes = None


def init_cache():
	# global cache_images
	# global cache_vocab_estampes
	# global cache_lieux
	# global cache_corpus
	# global cache_personnes

	parser = argparse.ArgumentParser()
	parser.add_argument("--cache")
	parser.add_argument("--cache_corpus")
	parser.add_argument("--cache_personnes")
	parser.add_argument("--cache_lieux")
	parser.add_argument("--cache_vocab_estampes")
	args = parser.parse_args()

	cache = Cache(args.cache)
	if args.cache_corpus:
		cache_corpus = Cache(args.cache_corpus)
	if args.cache_personnes:
		cache_personnes = Cache(args.cache_personnes)
	if args.cache_lieux:
		cache_lieux = Cache(args.cache_lieux)
	if args.cache_vocab_estampes:
		cache_vocab_estampes = Cache(args.cache_vocab_estampes)