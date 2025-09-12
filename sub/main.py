from worker import EmailNotificationSubscriber


def main():
    print('Starting Email Notification Subscriber...')
    subscriber = EmailNotificationSubscriber("email_notifications_channel")
    subscriber.listen()


if __name__ == "__main__":
    main()