# What is it?

ForeWork as the name suggests is a Forensic Framework, whose main goal is to
help investigators to find relevant forensic evidence in the most efficient way
possible, depending on the computing resources at their disposal.

You can have a look at the early design at the [project draft](documentation/project_draft.pdf) and at the [literature review presentation](documentation/M1 - Literature review.pdf).

# But why?

I started ForeWork as my dissertation project for the M.Sc. in Digital Investigations
and Computer Forensics at UCD (University College Dublin), in March 2016.

# Installation

## Install the requirements

* Python 3
* The Sleuth kit (instal it the way you prefer, e.g. with `brew` on OS X)
* Several python modules, listed in requirements.txt. Install them with `pip install -r requirements.txt`

## Then install ForeWork

```bash
python3 setup.py install
```

# Running tests

Requires `pytest` and `pytest-cov`. Run:

```bash
py.test -v --cov=forework
```

Note: ForeWork will soon be available on pypi, so that the installation will
boild down to install The Sleuth Kit and then run `pip install forework`. But
we're not there yet.

# And who the hell are you?

I am Andrea Barberio, you can find more information about me at
https://insomniac.slackware.it
