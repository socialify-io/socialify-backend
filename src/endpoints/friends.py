from sqlalchemy.sql.functions import user
from app import app, HTTP_METHODS, route, mongo_client 
from flask import Flask, render_template, request, jsonify
import json

# Database
from bson.objectid import ObjectId

# Helpers
from ..helpers.get_headers import get_headers, with_device_id, without_device_id
from ..helpers.verify_authtoken import verify_authtoken
from ..helpers.RSA_helper import verify_sign

# Crypto
import base64

# Datatime
from datetime import datetime
import pytz

# Models
from models.errors._api_error import ApiError

from models.responses._error_response import ErrorResponse
from models.responses._response import Response
from models.errors.codes._error_codes import Error

@app.route(f'{route}/sendFriendRequest', methods=['POST'])
async def send_friend_request():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required request headers not found.'
        ).__dict__

        return jsonify(ErrorResponse(
            error=error).__dict__)

    if verify_authtoken(headers, 'sendFriendRequest'):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        try:
            #user_username = user_session.query(User.username).filter(User.id == user_id).one()[0]
            user_username = mongo_client.users.find_one({"_id": ObjectId(user_id)})["username"]

        except:
            error = ApiError(
                code=Error().InvalidDeviceId,
                reason='Device id is not valid. Device may be deleted.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)

        # pub_key = user_session.query(Device.pubKey).filter(Device.userId ==
        #                                                    user_id, Device.id == device_id).one()

        pub_key = mongo_client.devices.find_one({"_id": ObjectId(device_id)})["pubKey"]

        if verify_sign(request, pub_key, 'sendFriendRequest'):
            body = request.get_json(force=True)
            date = datetime.utcfromtimestamp(headers['Timestamp']).replace(tzinfo=pytz.utc)

            # new_request = FriendRequest(
            #     receiverId=body['userId'],
            #     requesterId=user_id,
            #     requesterUsername=user_username,
            #     requestDate=date
            # )

            new_request = {
                "receiverId": body['userId'],
                "requesterId": user_id,
                "requesterUsername": user_username,
                "requestDate": date
            }

            mongo_client.friend_requests.insert_one(new_request)

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)


@app.route(f'{route}/fetchPendingFriendsRequests', methods=['GET'])
async def fetch_pending_friends_requests():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(error=error).__dict__)

    if verify_authtoken(headers, 'fetchPendingFriendsRequests'):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        #pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()
        pub_key = mongo_client.devices.find_one({"_id": ObjectId(device_id)})["pubKey"]

        if verify_sign(request, pub_key, 'fetchPendingFriendsRequests'):
            #requests = list(user_session.query(FriendRequest).filter(FriendRequest.receiverId == user_id).all())
            requests = mongo_client.friend_requests.find({"receiverId": ObjectId(user_id)})
            for index, friend_request in enumerate(requests):
                requests[index] = {
                    'id': friend_request.id,
                    'receiverId': friend_request.receiverId,
                    'requesterId': friend_request.requesterId,
                    'requesterUsername': friend_request.requesterUsername,
                    'requestDate': friend_request.requestDate
                }

            return jsonify(Response(data=requests).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

@app.route(f'{route}/acceptFriendRequest', methods=['POST'])
async def accept_friend_request():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(error=error).__dict__)

    if verify_authtoken(headers, 'acceptFriendRequest'):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        #pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()
        pub_key = mongo_client.devices.find_one({"_id": ObjectId(device_id)})["pubKey"]

        if verify_sign(request, pub_key, 'acceptFriendRequest'):
            body = request.get_json()
            requestId = body['requestId']
            # inviter = user_session.query(FriendRequest.requesterId).filter(FriendRequest.id == requestId).one()[0]
            # invited = user_session.query(FriendRequest.receiverId).filter(FriendRequest.id == requestId).one()[0]

            # new_friendship = Friendship(
            #     inviter=inviter,
            #     invited=invited
            # )

            # user_session.add(new_friendship)
            # user_session.query(FriendRequest).filter(FriendRequest.id == requestId).delete()
            # user_session.commit()

            mongo_client.friendships.insert_one({
                "inviter": mongo_client.friend_requests.find_one({"_id": ObjectId(requestId)})["requesterId"],
                "invited": user_id
            })
                
            mongo_client.friend_requests.delete_one({"_id": ObjectId(requestId)})

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

@app.route(f'{route}/fetchFriends', methods=['GET'])
async def fetch_friends():
    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(error=error).__dict__)

    if verify_authtoken(headers, 'fetchFriends'):
        body = request.get_json()
        user_id = body["userId"]

        # friendships_ids = [id[0] for id in user_session.query(Friendship.invited).filter(Friendship.inviter == user_id)]
        # friendships_ids += [id[0] for id in user_session.query(Friendship.inviter).filter(Friendship.invited == user_id)]
        friendships_ids = [id["invited"] for id in mongo_client.friendships.find({"inviter": user_id})]
        friendships_ids += [id["inviter"] for id in mongo_client.friendships.find({"invited": user_id})]

        friendships = []

        for id in friendships_ids:
            friendships.append({
                'id': id,
                #'username': user_session.query(User.username).filter(User.id == id).one()[0]
                'username': mongo_client.users.find_one({"_id": ObjectId(id)})["username"]
            })

        return jsonify(Response(data=friendships).__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

@app.route(f'{route}/removeFriend', methods=['POST'])
async def remove_friend():
    try:
        headers = get_headers(request, with_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(error=error).__dict__)

    if verify_authtoken(headers, 'removeFriend'):
        user_id = headers["UserId"]
        device_id = headers["DeviceId"]

        #pub_key = user_session.query(Device.pubKey).filter(Device.userId == user_id, Device.id == device_id).one()
        pub_key = mongo_client.devices.find_one({"_id": ObjectId(device_id)})["pubKey"]

        if verify_sign(request, pub_key, 'removeFriend'):
            body = request.get_json()
            delete_user_id = body['userId']

            # user_session.query(Friendship).filter(Friendship.inviter == user_id,
            #                                       Friendship.invited == delete_user_id).delete()
            # user_session.query(Friendship).filter(Friendship.inviter == delete_user_id,
            #                                       Friendship.invited == user_id).delete()

            mongo_client.friendships.delete_many({"$or": [{"inviter": user_id, "invited": delete_user_id}, {"inviter": delete_user_id, "invited": user_id}]})

            return jsonify(Response(data={}).__dict__)

        else:
            error = ApiError(
                code=Error.InvalidSignature,
                reason='Invalid signature.'
            ).__dict__

            return jsonify(ErrorResponse(
                error=error).__dict__)
    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

@app.route(f'{route}/getMutualFriends', methods=['GET'])
async def get_mutual_friends():
    try:
        headers = get_headers(request, without_device_id)

    except:
        error = ApiError(
            code=Error().InvalidHeaders,
            reason='Some required headers not found.'
         ).__dict__

        return jsonify(ErrorResponse(error=error).__dict__)

    if verify_authtoken(headers, 'getMutualFriends'):
        body = request.get_json()
        users = body['users']

        if len(users) != 1:
            error = ApiError(
                code=Error().InvalidNumberOfUsers,
                reason='Invalid of users in array is invalid. Please insert into table only 2 users.'
            ).__dict__

        friends = {}
        mutual_friends = []

        for user in users:
            #user_object = user_session.query(User).filter(User.id == user).one()
            user_object = mongo_client.users.find_one({"_id": ObjectId(user)})
            user_json = {
                'id': user_object['_id'],
                'username': user_object['username'],
               # 'avatar': str(user_object.avatar)
            }

            # friends_for_user = {id[0] for id in user_session.query(Friendship.invited).filter(Friendship.inviter == user)}
            # friends_for_user.update({id[0] for id in user_session.query(Friendship.inviter).filter(Friendship.invited == user)})
            friends_for_user = [id["invited"] for id in mongo_client.friendships.find({"inviter": user})]
            friends_for_user += [id["inviter"] for id in mongo_client.friendships.find({"invited": user})]
            friends.update({user: friends_for_user})

        mutual_friends.append(friends[users[1]].intersection(friends[users[2]]))


        print(mutual_friends)

        return jsonify(Response(data={}).__dict__)

    else:
        error = ApiError(
            code = Error().InvalidAuthToken,
            reason = 'Your authorization token is not valid.'
        ).__dict__

        return jsonify(ErrorResponse(
                    error=error).__dict__)

