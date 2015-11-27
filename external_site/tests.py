# -*- coding:utf-8 -*-
from datetime import date
from django.test import TestCase
from external_site.utils.tour import _get_month_days, _get_weeks, get_calendar


class TourTestCase(TestCase):

    def test_get_month_days(self):
        data = [
            [date(2015, 12, 13), 31],
            [date(2015, 11, 30), 30],
            [date(2016, 2, 1), 29]
        ]
        for i in data:
            self.assertEqual(list(_get_month_days(i[0]))[-1], i[1])


    def test_get_weeks(self):
        self.assertEqual(_get_weeks(0, range(1,16), [False, False, False]), [
            [[1, True], [2, True], [3, False], [4, False]],
            [[5, True], [6, True], [7, True], [8, True], [9, True], [10, False], [11, False]],
            [[12, True], [13, True], [14, True], [15, True]]
        ])


    def test_get_caledar(self):
        data = get_calendar(date(2015, 9, 15))
        self.assertEqual(data['month'], 'Сентябрь')
        self.assertEqual(data['offset'], [False])
        self.assertEqual(data['weeks'], [
                [[1, False], [2, False], [3, False], [4, False], [5, False], [6, False]],
                [
                    [7, False], [8, False], [9, False], [10, False],
                    [11, False], [12, False], [13, False]
                ],
                [
                    [14, False], [15, False], [16, True], [17, True],
                    [18, True], [19, False], [20, False]
                ],
                [
                    [21, True], [22, True], [23, True], [24, True],
                    [25, True], [26, False], [27, False]
                ],
                [[28, True], [29, True], [30, True]]
        ])
