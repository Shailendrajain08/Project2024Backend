# HireCoderApi

Based on Django `4.2.4`

## Getting Started

Setup project environment with [virtualenv](https://virtualenv.pypa.io) and [pip](https://pip.pypa.io).

```bash
$ virtualenv project-env
$ source project-env/bin/activate
```

### Installation

1. Clone the repo
    ```sh
    git clone https://github.com/hirecoderdev/backend_restructure.git
    ```

2. Install requirements by running this command from your project dir
    ```bash

    # On Dev:
    $ pip install -r requirements/dev.txt

    # On Prod:
    $ pip install -r requirements.txt

    # get the latest .env from your fellow developer, or copy same from dotenvsample.
    $ touch backend_restructure/.env
    ```

3. At this point in time this application works with postgres, Setup these environment variables on your system (or in .env file)


    * On Windows

        ```sh
        set "DEBUG=True"
        set "DJANGO_SETTINGS_MODULE=mysite.settings"
        set "SECRET_KEY=xxxxxYourxxSecretxxKeyxxxxx"
        set "DATABASE_URL=psql://username:password@127.0.0.1:5432/dbname"
        ```

    * On Linux

        ```bash
        export DEBUG='TRUE'
        export DJANGO_SETTINGS_MODULE='mysite.settings'
        export SECRET_KEY='xxxxxYourxxSecretxxKeyxxxxx'
        export DATABASE_URL='psql://username:password@127.0.0.1:5432/dbname'
        ```
4. Apply Migrations by running this command from the project dir

    ```pythonn
    python manage.py migrate
    ```

5. Create a superuser using [this guide](https://www.geeksforgeeks.org/how-to-create-superuser-in-django/).

6. Finally run your dev server by running this command from your project dir

    ```python
    python manage.py runserver
    ```

# Goodies Included #
1. Seprate settings for development and production environment
2. Settings based on [django-environ](https://django-environ.readthedocs.org/en/latest/)
3. Excellent admin interface by [django-grappelli](https://django-grappelli.readthedocs.org/en/latest/index.html)
4. Static file serving with [whitenoise](https://github.com/evansd/whitenoise)
5. Extra commands by [django-extensions](https://github.com/django-extensions/django-extensions)

### Help ###
1. Use this to generate [SECRET_KEY](http://www.miniwebtool.com/django-secret-key-generator/)

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request