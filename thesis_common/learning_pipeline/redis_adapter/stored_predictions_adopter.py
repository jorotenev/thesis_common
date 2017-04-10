from .redis_adaptor import RedisAdapter
from .utils import key, get_non_venue_part_of_key
from dateutil.parser import parse

class StoredPredictionsAdapter(RedisAdapter):
    # this tag is used together with the name of the venue
    # to form a key, under which the keys of the predictions for a venue are added. see _add_avaialable_predictions()
    _predictions_stack_tag = 'predictions'

    def __init__(self, *args, **kwargs):
        super(StoredPredictionsAdapter, self).__init__(*args, **kwargs)

    def store_predictions(self, venue, datetime_newest_training, predictions):
        """
        Store the predictions for this venue for this datetime.
        The values are stored under a composite key of the venue and the iso string representation of the datetime

        :param venue:
        :param datetime_newest_training: datetime object, with which we label the set of predictions. It is the
        datetime of the newest entry used to train the model(s) used when making the prediction.
        :param predictions: json string. the json is a map between a datetime and a number
        (the number is the prediction for this datetime)
        :return: None
        :raises ValueError - if the underlying redis db already has predictions for this venue and :datetime_newest_training
        """
        dt_str = datetime_newest_training.replace(microsecond=0).isoformat()
        # we will store the predictions under this key
        composite_key = key(venue, dt_str)

        # set will be successful only if the key doesn't exist, because of nx=True flag
        set_is_successfull = self.r.set(composite_key, predictions, nx=True)
        if set_is_successfull:
            self._add_avaialable_predictions(venue=venue, prediction_key=composite_key)
        else:
            raise ValueError("Key {key} is already present in the redis db.".format(key=composite_key))

    def _add_avaialable_predictions(self, venue, prediction_key):
        """
        store_predictions() uses redis SET function. set() doesn't have any ordering guarantees, so it will be
        expensive to know which was the last collection of predictions stored by store_predictions().
        So to make it easier to know which was the last added set of predictions, we add the key which was used
        to store the predictions,to a separate data structure (sort of like a stack?) so it's O(1) to get the key
        of the newest set of predictions for a venue.

        :param prediction_key: the key used to store the prediction.
        :return: None
        """
        self.enqueue(self.r)(key(venue, self._predictions_stack_tag), prediction_key)

    def get_keys_of_available_predictions_for_venue(self, venue):
        """
        For this :venue, there are a number of sets of predictions available. Each set is predictions for a period of time.
        This functions returns the keys for the sets of predictions.
        See _add_avaialable_predictions().
        :return: list of keys. Agains each of these keys there's a set of predictions. The first element is the newest key
        """
        k = key(venue, self._predictions_stack_tag)
        # return all elements of the list (range over the whole list)
        return self.r.lrange(k, 0, self.r.llen(k))

    def get_key_of_newest_predictions(self, venue):
        """
        Like get_keys_of_available_predictions_for_venue() but only returns the first key.
        See _add_avaialable_predictions().
        :param venue:
        :return: the newest key, holding predictions, added for this venue. None if there are no predictions for this venue
        """
        return self.r.lindex(key(venue, self._predictions_stack_tag), 0)

    def get_predictions(self, predictions_key):
        """
        Given a **single** key, returned from  `get_key_of_newest_predictions()` or `get_keys_of_available_predictions_for_venue()`,
        return a the predictions stored under this key. Normally the predictions are for a fixed period of time.
        The key has encoded the venue and the timestamp of the newest timestmap used to train the model, which produced the predictions.

        :returns The funciton returns a tuple, where the first element is the timestamp of the newest training entry, and the second is a json encoded string.
        """

        predictions = self.r.get(predictions_key)
        # we have the JSON with timestamp-prediction pairs.
        # Let's also return the datetime, which is encoded within the key
        dt_str = get_non_venue_part_of_key(predictions_key)
        dt_obj = parse(dt_str)
        return  (dt_obj, predictions)
        
