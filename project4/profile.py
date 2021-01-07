class Profile:
    def __init__(
            self,
            *,
            id,
            name,
            about,
            rating,
            picture,
            price,
            goals,
            free
    ):
        self.id = id
        self.name = name
        self.about = about
        self.rating = rating
        self.picture = picture
        self.price = price
        self.goals = goals
        self.free = free

    @property
    def free_days_in_week(self):
        """
        Keep only free hours in week day
        """
        def _keep_free_time(s):
            return [h for h, v in s.items() if v]
        return {d: _keep_free_time(s) for d, s in self.free.items()}
