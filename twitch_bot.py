import twitchio, random, requests, os
from twitchio.ext import pubsub

CLIENT_ID = 'CLIENT_ID'
USER_OAUTH_TOKEN = 'USER_OAUTH_TOKEN'
USER_CHANNEL_ID = 'USER_CHANNEL_ID' # Must be integer
MODERATOR_ID = 'MODERATOR_ID[' # Must be integer

client = twitchio.Client(token=USER_OAUTH_TOKEN, initial_channels=['CHANNEL_NAME'])
client.pubsub = pubsub.PubSubPool(client)

broadcaster = client.create_user(USER_CHANNEL_ID, 'CHANNEL_NAME')

vips = []
mods = [] # List of mods
whitelist = [] # List of people,
timeout_text = [] # List of timeout text to send.
emotes = [] # List of 7TV Emotes


async def create_main_reward():
    await broadcaster.create_custom_reward(token=USER_OAUTH_TOKEN,
                                           enabled=True,
                                           title='Steal VIP',
                                           cost=35000,
                                           prompt='Reward description',
                                           max_per_user_per_stream=None,
                                           max_per_stream=48,
                                           global_cooldown=1800,
                                           input_required=True)

async def edit_reward():
    main_reward = (await broadcaster.get_custom_rewards(token=USER_OAUTH_TOKEN, only_manageable=True))[0]
    await main_reward.edit(token=USER_OAUTH_TOKEN, enabled=False, paused=True)

async def delete_reward():
    main_reward = (await broadcaster.get_custom_rewards(token=USER_OAUTH_TOKEN, only_manageable=True))[0]
    await main_reward.delete(token=USER_OAUTH_TOKEN)

async def steal_vip_event(random_number, id, name, vip_id, vip_name, vips_2, reward_redemption, main_reward):
            if 2 <= random_number <= 13:
                await broadcaster.add_channel_vip(token=USER_OAUTH_TOKEN, user_id=id)
                await broadcaster.channel.send(content=f'{name} stole vip from {vip_name.lower()} peepoBANDOS')
                vips.remove([vip_name, vip_id])
                vips_2.remove(vip_name)
                vips_2.remove(vip_id)
                await broadcaster.remove_channel_vip(token=USER_OAUTH_TOKEN, user_id=vip_id)
                await reward_redemption[0].fulfill(token=USER_OAUTH_TOKEN)
                set_cooldown(time=1800, main_reward=main_reward)
            elif 14 <= random_number <= 70:
                await broadcaster.timeout_user(token=USER_OAUTH_TOKEN, moderator_id=MODERATOR_ID, user_id=id, duration=3600, reason='Reward redemption')
                await broadcaster.channel.send(content=f'{name} tried to steal a VIP from {vip_name.lower()}, but {random.choice(timeout_text)} 1 hour {random.choice(emotes)}')
                await reward_redemption[0].fulfill(token=USER_OAUTH_TOKEN)
                set_cooldown(time=1800, main_reward=main_reward)
            elif 71 <= random_number <= 100:
                await broadcaster.timeout_user(token=USER_OAUTH_TOKEN, moderator_id=MODERATOR_ID, user_id=id, duration=7200, reason='Reward redemption')
                await broadcaster.channel.send(content=f'{name} tried to steal a VIP from {vip_name.lower()}, but {random.choice(timeout_text)} 2 hours {random.choice(emotes)}')
                await reward_redemption[0].fulfill(token=USER_OAUTH_TOKEN)
                set_cooldown(time=1800, main_reward=main_reward)
            elif random_number == 1:
                await broadcaster.timeout_user(token=USER_OAUTH_TOKEN, moderator_id=MODERATOR_ID, user_id=id, duration=86400, reason='Получение награды')
                await broadcaster.channel.send(content=f'POLICE {name} pulled out a lucky ticket and {random.choice(timeout_text)} for 24 hours POLICE')
                set_cooldown(time=1800, main_reward=main_reward)

def common_data(user_input, vip_list, white_list):
    if '@' in user_input:
        user_input = user_input.replace('@', '')
        if user_input == '':
            user_input = 'INCORRECT_INPUT'
    for input in user_input.lower().split():
        for vip in vip_list:
            if input == vip:
                return input
        for member in white_list:
            if input == member:
                return input
        for value in ['random']:
            if input == value:
                return input
    return input

def set_cooldown(time: int, main_reward):
    head = {'Client-Id': f'{CLIENT_ID}',
            'Authorization': f'Bearer {USER_OAUTH_TOKEN}',
            'Content-Type': 'application/json'}
    payload = {'is_global_cooldown_enabled': True,
               'global_cooldown_seconds': time}
    url = f'https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={USER_CHANNEL_ID}&id={main_reward.id}'
    r = requests.patch(url, params=payload, headers=head)
    print(f'STATUS CODE: {r.status_code}\n')

@client.event()
async def event_ready():
    print(f'Logged in as | {client.nick}')
    print(f'User id is | {client.user_id}')

@client.event()
async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
    message = f'ID: {event.user.id}\nUsername: {event.user.name}\nReward Title: {event.reward.title}\nReward Cost: {event.reward.cost}'
    print(message)

    main_reward = (await broadcaster.get_custom_rewards(token=USER_OAUTH_TOKEN, only_manageable=True))[0]

    for vip in await broadcaster.fetch_channel_vips(token=USER_OAUTH_TOKEN, first=100):
        if [vip.name, vip.id] not in whitelist:
            if [vip.name, vip.id] not in vips:
                vips.append([vip.name.lower(), vip.id])

    vips_2 = [item for a_list in vips for item in a_list]
    whitelist_2 = [item for a_list in whitelist for item in a_list]

    if event.reward.title == 'REWARD_TITLE':
        vip_name_to_steal = None
        reward_redemption = await event.reward.get_redemptions(token=USER_OAUTH_TOKEN, status='UNFULFILLED', first=50)
        vip_name_to_steal = common_data(user_input=reward_redemption[0].input, vip_list=vips_2, white_list=whitelist_2)
        print(f'VIP NAME TO STEAL COMMON DATA: {vip_name_to_steal}')
        if vip_name_to_steal.lower() in vips_2:
            vip_id_to_steal = vips_2[vips_2.index(vip_name_to_steal.lower()) + 1]
        elif vip_name_to_steal.lower() in whitelist_2:
            vip_name_to_steal = vip_name_to_steal.lower()
        elif vip_name_to_steal.lower() in ['random']:
            vip_name_to_steal = 'random'
        else:
            vip_name_to_steal = reward_redemption[0].input

    random_vip = random.choice(vips)
    random_vip_name = random_vip[0]
    random_vip_id = random_vip[1]
    random_number = random.randint(1, 100)

    print(f'RANDOM NUMBER: {random_number}')
    print(f'RANDOM VIP NAME: {random_vip_name}')
    print(f'RANDOM VIP ID: {random_vip_id}')

    if event.reward.title == 'REWARD_TITLE':
        if ([event.user.name.lower(), event.user.id] in vips) or ([event.user.name.lower(), event.user.id] in whitelist):
            await broadcaster.channel.send(content=f'{event.user.name}, you already have a VIP! Points returned, cooldown rewards reset!')
            await reward_redemption[0].refund(token=USER_OAUTH_TOKEN)
            set_cooldown(time=1, main_reward=main_reward)
        elif event.user.name.lower() in mods:
            await broadcaster.channel.send(content=f'{event.user.name}, moderators are not allowed to claim VIP :( Points returned, cooldown  reset!')
            await reward_redemption[0].refund(token=USER_OAUTH_TOKEN)
            set_cooldown(time=1, main_reward=main_reward)
        else:
            if vip_name_to_steal.lower() == 'random':
                await steal_vip_event(
                    random_number=random_number,
                    id=event.user.id,
                    name=event.user.name,
                    vip_id=random_vip_id,
                    vip_name=random_vip_name.lower(),
                    vips_2=vips_2,
                    reward_redemption=reward_redemption,
                    main_reward=main_reward
                    )
            else:
                if (vip_name_to_steal.lower() not in vips_2) and ((vip_name_to_steal.lower() not in whitelist_2)):
                    await broadcaster.channel.send(content=f'{event.user.name}, there is no such user among VIPs! Alas, your points are burned Jkrg')
                    await reward_redemption[0].fulfill(token=USER_OAUTH_TOKEN)
                    set_cooldown(time=1800, main_reward=main_reward)
                elif vip_name_to_steal.lower() in whitelist_2:
                    await broadcaster.channel.send(content=f'{event.user.name}, VIP {vip_name_to_steal.lower()} under the protection of the Almighty and it is impossible to steal VIP from him! Points returned, cooldown rewards reset!')
                    await reward_redemption[0].refund(token=USER_OAUTH_TOKEN)
                    set_cooldown(time=1, main_reward=main_reward)
                elif vip_name_to_steal.lower() in vips_2:
                    await steal_vip_event(
                        random_number=random_number,
                        id=event.user.id,
                        name=event.user.name,
                        vip_id=vip_id_to_steal,
                        vip_name=vip_name_to_steal.lower(),
                        vips_2=vips_2,
                        reward_redemption=reward_redemption,
                        main_reward=main_reward
                        )
async def main():
    topics = [
        pubsub.channel_points(USER_OAUTH_TOKEN)[USER_CHANNEL_ID]
    ]
    await client.pubsub.subscribe_topics(topics)
    await client.start()

client.loop.run_until_complete(main())