from dotenv import load_dotenv
from telebot import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.util import antiflood, extract_arguments, quick_markup
import os
import requests
from db import UsersData, Products, Orders
from datetime import datetime
import re
import json
import func

load_dotenv()

api_key = os.getenv('API_KEY')
print(api_key)

now = datetime.now()

ADMIN_ADDRESS = '0x8e6C37BA15fb4a4013Ef78554C40A7ed7EddF4c7'

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN, 'Markdown', disable_web_page_preview= True)

bot_info = bot.get_me()

user_db = UsersData()
user_db.setup()

prod_db = Products()
prod_db.setup()

order_db = Orders()
order_db.setup()


def get_hash(link: str):
    pattern = r"(?<=tx\/)[\w\d]+"
    match = re.search(pattern, link)
    
    if match:
        tx_hash = match.group(0)
        return tx_hash
    else:
        return 0


def get_username(user_id):
    try:
        user = bot.get_chat(user_id)
        if user.username:
            return user.username
        else:
            return user.first_name
    except Exception as e:
        print(e)
        return None
    

def get_chain_price(chain: str):
    btc = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    sol = "So11111111111111111111111111111111111111112"
    eth = '0x2170Ed0880ac9A755fd29B2688956BD959F933F8'
    if chain == 'bitcoin':
      url = f"https://api.dexscreener.com/latest/dex/tokens/{btc}"
      response = requests.get(url)
      if response.status_code == 200:
          mc = response.json()['pairs'][2]['priceUsd']
          
          return float(mc)
        
    elif chain == 'solana':
      url = f"https://api.dexscreener.com/latest/dex/tokens/{sol}"
      response = requests.get(url)
      if response.status_code == 200:
          mc = response.json()['pairs'][0]['priceUsd']
          
          return float(mc)
        
    elif chain == 'ethereum':
      url = f"https://api.dexscreener.com/latest/dex/tokens/{eth}"
      response = requests.get(url)
      if response.status_code == 200:
          mc = response.json()['pairs'][0]['priceUsd']
          
          return float(mc)
    else:
        return "failed to connect try again later"
    
#Dev commands 

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    print(message.from_user.id)
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        send = bot.send_message(message.chat.id,"Enter message to broadcast")
        bot.register_next_step_handler(send,sendall)
        
    else:
        bot.reply_to(message, "You're not allowed to use this command")
        
        
        
def sendall(message):
    users = user_db.get_users()
    for chatid in users:
        try:
            msg = antiflood(bot.send_message, chatid, message.text)
        except Exception as e:
            print(e)
        
    bot.send_message(message.chat.id, "done")
    

@bot.message_handler(commands=['userno'])
def userno(message):
    print(message.from_user.id)
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        x = user_db.get_users()
        bot.reply_to(message,f"Total bot users: {len(x)}")
    else:
        bot.reply_to(message, "admin command")
        
        
@bot.message_handler(commands=['addproduct'])
def addproduct(message):
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        bot.send_message(messager, "Send Product details as follows\n`productid` , `name` , `price`, `loaction` , `description` , `type`")
        bot.register_next_step_handler(message, set_product)
    else:
        bot.reply_to(message, "admin command")
        
        
def set_product(message):
    msg = str(message.text).split(",")
    pid = msg[0]
    name = msg[1]
    location = msg[3]
    price = msg[2]
    description = msg[4]
    type = msg[5]
    try:
        prod_db.add_product(pid, name, price, location, description, type)
        bot.reply_to(message, "Added successfully")
    except Exception as e:
        bot.reply_to(message, e)
        
        
@bot.message_handler(commands=['adminallproducts'])
def allproduct(message):
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        products = prod_db.get_all_products()
        msg = "*All Product*\n\n"
        for prod in products:
            msg +=f"`{prod[0]}` : *{prod[1]}, ${prod[2]}, {prod[3]}, {prod[4]}, type: {prod[5]}*\n\n"
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton('Delete Product', callback_data='deleteproduct')
        markup.add(btn)
        bot.send_message(message.chat.id, msg, reply_markup=markup)    
    else:
        bot.reply_to(message, "admin command")
        

# Dictionary to track the current product index for each user
user_product_index = {}

@bot.message_handler(commands=['allproducts'])
def all_product(message):
    try:
        # Fetch all products from the database
        products_ = prod_db.get_all_products()
        
        if not products_:
            bot.send_message(message.chat.id, "No product available at the moment\nTry again later")
            return
        
        # Initialize the user's product index to 0
        user_product_index[message.chat.id] = 0
        current_index = 0

        # Display the first product
        product = products_[current_index]
        msg = f"*All Product*\n\n`{product[0]}` \n\n *{product[1]}, ${product[2]}, {product[3]}, {product[4]}, type: {product[5]}*\n\n"
        
        # Define inline keyboard markup
        markup = quick_markup({
            'Buy this Product': {'callback_data': 'proceed'},
            'Close': {'callback_data': 'cancel'},
            'Next': {'callback_data': 'nextall'}
        }, 3)
        
        # Send the message with the first product
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "An error occurred while fetching products.\nPlease try again later.")

@bot.callback_query_handler(func=lambda call: call.data == 'nextall')
def next_product(call):
    try:
        products_ = prod_db.get_all_products()
        current_index = user_product_index.get(call.message.chat.id, 0) + 1
        if current_index >= len(products_):
            current_index = 0

        user_product_index[call.message.chat.id] = current_index
        
        product = products_[current_index]
        print(product[0])
        msg = f"*All Product*\n\n`{product[0]}` \n\n *{product[1]}, ${product[2]}, {product[3]}, {product[4]}, type: {product[5]}*\n\n"

        markup = quick_markup({
            'Buy this Product': {'callback_data': 'proceed'},
            'Close': {'callback_data': 'cancel'},
            'Next': {'callback_data': 'nextall'}
        }, 3)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, "An error occurred. Please try again.")

     
@bot.message_handler(commands=['delproduct'])
def delproduct(message):
    messager = message.chat.id
    if str(messager) == "7034272819" or str(messager) == "6219754372":
        try:
            pid = extract_arguments(message.text)
            prod_db.delete_product(pid)
            bot.send_message(message.chat.id, 'Done')
        except Exception as e:
            bot.send_message(message.chat.id, e)
        
    else:
        bot.reply_to(message, "admin command")  
        
@bot.message_handler(commands=['start'])
def start(message):
    owner = message.chat.id
    user_db.add_user(owner)
    msg = """
Welcome to *HostGenius VPS*!

Hello and welcome to HostGenius VPS, your ultimate solution for reliable, high-performance Virtual Private Servers (VPS). Our advanced VPS hosting services are designed to cater to all your hosting needs, whether you're a developer, a business owner, or just someone in need of robust and scalable server solutions.

Our bot is here to assist you every step of the way. From selecting the perfect VPS plan to managing and optimizing your server, HostGenius VPS ensures a seamless and efficient experience.

Experience the power, speed, and flexibility of our VPS hosting. Let's get started and take your online presence to the next level with HostGenius VPS!   
    
    """
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('Buy A Server', callback_data='buy')
    btn1 = InlineKeyboardButton('See all servers', callback_data='allservers')
    markup.add(btn, btn1)
    bot.send_message(owner, msg, reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    pass
            
    
@bot.callback_query_handler(func= lambda call: True)
def call_back(call):
    owner = call.message.chat.id
    
    if call.data == 'deleteproduct':
        delproduct(call.message)
        
        
    elif call.data == 'allservers':
        all_product(call.message)
        
        
    elif call.data == 'cancel':
        bot.delete_message(owner, call.message.message_id)
        
        
    elif call.data == 'buy':
        all_product(call.message)
    
    elif call.data == 'shared':
        all_products = prod_db.get_all_products()
        msg = "*Exodus Hosts* \n\n💡 Copy the Server id to proceed with your order\n\n"
        for prod in all_products:
            msg += f"`{prod[0]}` : *{prod[1]}, ${prod[2]}, {prod[3]}, {prod[4]}, type: {prod[5]}*\n\n"
        markup = InlineKeyboardMarkup()
        b = InlineKeyboardButton('Proceed', callback_data='proceed')
        markup.add(b)
        bot.send_message(owner, msg, reply_markup=markup)
        
        
    elif call.data == 'proceed':
        s = bot.send_message(owner, "Enter Server ID: ")
        bot.register_next_step_handler(s, start_buy)
        
        
    elif call.data == 'pay':
        order = order_db.get_orders_by_user(owner)
        y = len(order)-1
        name = order[y][1]
        price = order[y][2]
        msg = f"""HostGenius VPS
        
Select your preferred payment method for {name}

You are required to pay `${price}` to complete your order

        """
        
        markup = quick_markup({
            'Ethereum': {'callback_data': 'ethereum'},
        })
        
        bot.send_message(owner, msg, reply_markup=markup)
        
        
    elif call.data == 'verify':
        order = order_db.get_orders_by_user(owner)
        y = len(order)-1
        name = order[y][1]
        price = order[y][2]
        msg = f"""HostGenius VPS

Make a payment of $`{price}` to 

`0x0f263d3Fc1306780627B1d7B605FC872C653f80a` 

for order:

Order-id: #{order[y][0]}  
Product Name: {name} 
Order Name: {order[y][5]} 
Order Date: {order[y][3]}   

Payment Status: {'Unpaid' if order[y][4] == 0 else 'Paid'}
        
        """
        #bot.send_message("7034272819", f"NEW PAYMENT\n\n{msg}")
        s = bot.send_message(owner, "please send full etherscan transaction link for verification")
        bot.register_next_step_handler(s, pay_verify)
        
        
    elif call.data == 'ethereum' or call.data == 'usdt':
        order = order_db.get_orders_by_user(owner)
        y = len(order)-1
        name = order[y][1]
        price = order[y][2]
        msg = f"""HostGenius VPS

Make a payment of $`{price}` to 

`0x0f263d3Fc1306780627B1d7B605FC872C653f80a` 

for order:

Order-id: #{order[y][0]}  
Product Name: {name} 
Order Name: {order[y][5]} 
Order Date: {order[y][3]}   

Payment Status: {'Unpaid' if order[y][4] == 0 else 'Paid'}

*Click the verify payment button below to check order status*
        
        """
        markup = quick_markup({
            'Verify Payment': {'callback_data': 'verify'}
        })
        bot.send_message(owner, msg, reply_markup=markup)
        
        
        
    
    elif call.data == 'solana':
        order = order_db.get_orders_by_user(owner)
        y = len(order)-1
        name = order[y][1]
        price = order[y][2]
        msg = f"""HostGenius VPS

Make a payment of $`{price}` to 

`P3sbkDB3tv3Fo9Ty74SHQX1LPpYQrKQwnDC5U4A7gPv` 

for order:

Order-id: #{order[y][0]}  
Product Name: {name} 
Order Name: {order[y][5]} 
Order Date: {order[y][3]}   

Payment Status: {'Unpaid' if order[y][4] == 0 else 'Paid'}

*Click the verify payment button below to check order status*
        
        """
        markup = quick_markup({
            'Verify Payment': {'callback_data': 'verify'}
        })
        bot.send_message(owner, msg, reply_markup=markup)
        
        
    elif call.data == 'token':
        order = order_db.get_orders_by_user(owner)
        y = len(order)-1
        name = order[y][1]
        price = order[y][2]
        msg = f"""HostGenius VPS

Make a payment of $`{price}` to 

`P3sbkDB3tv3Fo9Ty74SHQX1LPpYQrKQwnDC5U4A7gPv` 

for order:

Order-id: #{order[y][0]}  
Product Name: {name} 
Order Name: {order[y][5]} 
Order Date: {order[y][3]}   

Payment Status: {'Unpaid' if order[y][4] == 0 else 'Paid'}

*Click the verify payment button below to check order status*
        
        """
        markup = quick_markup({
            'Verify Payment': {'callback_data': 'verify'}
        })
        bot.send_message(owner, msg, reply_markup=markup)

        
                
def start_buy(message):
    owner = message.chat.id
    try:
        server_details = prod_db.get_product(message.text)
    except Exception as e:
        bot.send_message(owner, "Invalid server ID")
    print(server_details)
    msg = f"""HostGenius VPS
    
    
Server-ID: {server_details[0][0]}
Type: {server_details[0][5]}
Name: {server_details[0][1]}
Price: ${server_details[0][2]}
Location: {server_details[0][3]}
    
Description: {server_details[0][4]}
    
*Do you want to buy this server?*
    """       
    markup = quick_markup({
        "Pay": {'callback_data':'pay'},
        'Cancel': {'callback_data':'cancel'}
    })
    bot.send_message(owner, msg, reply_markup=markup)
    id = server_details[0][0]
    date = now.strftime("%Y-%m-%d")
    name = f'{id}-{owner}-{date}'
    order_db.add_order(owner, id, date, ordername=name)
    y = order_db.get_orders_by_user(owner)
    bot.send_message("7034272819", f"NEW ORDER PLACED FOR {owner}\n\n{y}")
    
def pay_verify(message):
    owner = message.chat.id
    order = order_db.get_orders_by_user(owner)
    y = len(order)-1
    name = order[y][1]
    price = order[y][2]
    tx_link = message.text
    tx_hash = get_hash(tx_link)
    print(tx_hash)
    print(func.parse_tx(tx_hash))
    from_addr, to_addr, value = func.parse_tx(tx_hash)
    print(func.parse_tx(tx_hash))
    value_ = get_chain_price('ethereum')
    value_usd = value*value_
    if to_addr == ADMIN_ADDRESS:
        if value_usd >= price:
            bot.send_message(7034272819, f"New payment from {owner}\n\nPayment Link: {tx_link}")
        else:
            bot.send_message(owner, "Payment not enough ")
    
    else:
        bot.send_message(owner, "Error in payment")    
      
bot.infinity_polling()