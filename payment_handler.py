from main import dp, bot
from config_file.config import sberbank_payment

from aiogram.types import Message, ShippingOption, LabeledPrice

prices = [LabeledPrice(label='Подписка на 30 дней', amount=10000)]

shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add(LabeledPrice('Pickup', 300))]


@dp.message_handler(lambda message: message.text.startswith('/buy'))
def command_pay(message:Message):
    bot.send_invoice(
        chat_id= message.chat.id,
        title= 'Купить подписку',
        description= ' Want to visit your great-great-great-grandparents? Make a fortune at the races? Shake hands with Hammurabi and take a stroll in the Hanging Gardens? Order our Working Time Machine today!',
        invoice_payload = 'asdasd',
        provider_token = sberbank_payment,
        currency='RUB',
        prices = prices,
        photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
        photo_height=512,
        photo_width=512,
        photo_size=512,
        is_flexible=False,
        start_parameter='time-machine-example')



@dp.shipping_query_handler(lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@dp.pre_checkout_query_handler(lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@dp.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')

