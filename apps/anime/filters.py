ORDERING_FIELDS = (
    'rating',
    'translated_title',
    'total_episodes',
    'total_seasons',
    'release_date'
)

ORDERING_MAP = {
    'total_episodes': 'total_episodes',
    '-total_episodes': '-total_episodes',
    'total_seasons': 'total_seasons',
    '-total_seasons': '-total_seasons',
}