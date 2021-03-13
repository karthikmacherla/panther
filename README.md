# Panther

> A distributed web crawler written in python.

See [my post](http://karthikmacherla.codes/post/panther) for more info. 

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

## Requirements
Docker for Desktop

## Usage
`git clone` this repo

Run `docker-compose build` on your machine. Once the process is finished, run `docker-compose up` 
to start the service. 

URLs can be added to the frontier-queue via `localhost:5000`, and workers can be monitored via `localhost:5001`. Finally, the corpus of documents can be monitored via `localhost:5002`.


## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-shield]: https://img.shields.io/github/forks/karthikmacherla/panther?label=Forks&style=for-the-badge
[forks-url]: https://github.com/karthikmacherla/panther/network/members
[stars-shield]: https://img.shields.io/github/stars/karthikmacherla/panther?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/karthikmacherla/panther?style=for-the-badge
[issues-url]: https://github.com/karthikmacherla/panther/issues
[license-shield]: https://img.shields.io/github/license/karthikmacherla/panther?label=LICENSE&style=for-the-badge
[license-url]: https://github.com/karthikmacherla/panther/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/karthikmacherla
[product-screenshot]: images/screenshot.png