from django.test import TestCase

from orders.models import OrderModel, BlessingModel
from accounts.models import UserModel, USER_SEX_CHOICE


# Create your tests here.


class OrderTest(TestCase):
    def setUp(self):
        pass

    def test_save_order(self):
        u = UserModel()
        u.username = 'test'
        u.headimage = 'wefwef.jpg'
        u.sex = 'm'
        u.save()

        t = UserModel()
        t.username = 'target test'
        t.headimage = 'wefwefwef.jpg'
        t.sex = 'w'
        t.save()

        o = OrderModel()
        o.target_usermodel = t
        o.usermodel = u
        o.candies_count = 12
        o.city = '上海'
        o.order_content = '测试'
        o.wx_prepayid = "wx_prepayid"
        o.save()

        from orders.viewmodels import PostLoveSerializer, OrderSerializer
        s = PostLoveSerializer(o)

        print(s.data)

        orders = OrderModel.objects.all()
        ss = OrderSerializer(orders, many=True)
        print(ss.data)

        self.assertEqual(OrderModel.objects.count(), 1)
        self.assertEqual(OrderModel.objects.first().target_usermodel, t)
        self.assertEqual(OrderModel.objects.first().usermodel, u)
