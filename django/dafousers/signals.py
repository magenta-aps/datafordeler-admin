# -*- coding: utf-8 -*-
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from dafousers.models import EntityWithHistory, HistoryForEntity


@receiver(post_save)
def on_post_save(sender, instance, created, **kwargs):
    if issubclass(sender, EntityWithHistory):
        last_historic_item = sender.history_class.objects.filter(
            entity=instance
        ).order_by('updated').last()
        updated_dict = sender.history_class.get_history_data_dict(instance)

        if last_historic_item is None:
            # Created new item
            content_list = []
            for key, value in updated_dict.iteritems():
                if key not in ['updated']:
                    if key == '_relations':
                        for relkey in value:
                            relvalues = [
                                unicode(x) for x in value[relkey].all()
                            ]
                            if len(relvalues) > 0:
                                content_list.append(
                                    "    %s: %s" %
                                    (relkey, ', '.join(relvalues))
                                )
                    else:
                        if 'password' in key:
                            value = '******'
                        content_list.append("    %s: %s" % (key, value))
            verbose_contents = '\n'.join(content_list)

            logging.getLogger('django.server').info(
                "\n".join([
                    "%s %s (id=%d) was created by %s",
                    "Contents:",
                    "%s"
                ]),
                instance.__class__.__name__,
                unicode(instance),
                instance.id,
                instance.changed_by,
                verbose_contents
            )

        else:
            # Updated existing item
            historic_dict = sender.history_class.get_history_data_dict(
                last_historic_item
            )
            difference = {}
            for key, value in updated_dict.iteritems():
                if value != historic_dict.get(key):
                    difference[key] = (historic_dict.get(key), value)

            diff_list = []
            for key, values in difference.iteritems():
                if key not in ['updated']:
                    (value1, value2) = values
                    if key == '_relations':
                        for relkey in value1:
                            relvalues1 = [
                                unicode(x) for x in value1[relkey].all()
                            ]
                            relvalues2 = [
                                unicode(x) for x in value2[relkey].all()
                            ]
                            if len(relvalues1) > 0 or len(relvalues2) > 0:
                                diff_list.append(
                                    "    %s: %s => %s" % (
                                        relkey,
                                        ', '.join(relvalues1),
                                        ', '.join(relvalues2)
                                    )
                                )
                    else:
                        if 'password' in key:
                            value1 = value2 = '******'
                        diff_list.append(
                            "    %s: %s => %s" % (key, value1, value2)
                        )
            verbose_difference = '\n'.join(diff_list)

            logging.getLogger('django.server').info(
                "\n".join([
                    "%s %s (id=%d) was updated by %s",
                    "Updates:",
                    "%s"
                ]),
                instance.__class__.__name__,
                unicode(instance),
                instance.id,
                instance.changed_by,
                verbose_difference
            )
