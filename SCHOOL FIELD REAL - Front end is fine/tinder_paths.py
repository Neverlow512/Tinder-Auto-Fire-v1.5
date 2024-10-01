# tinder_paths.py

TINDER_PATHS = {
    'habits': {
        'questions': {
            'drink_frequency': {
                'question': "//XCUIElementTypeStaticText[@value='How often do you drink?']",
                'options': {
                    'Not for me': "//XCUIElementTypeStaticText[@value='Not for me']",
                    'Sober': "//XCUIElementTypeStaticText[@value='Sober']",
                    'Sober curious': "//XCUIElementTypeStaticText[@value='Sober curious']",
                    'On special occasions': "//XCUIElementTypeStaticText[@value='On special occasions']",
                    'Socially on weekends': "//XCUIElementTypeStaticText[@value='Socially on weekends']",
                    'Most Nights': "//XCUIElementTypeStaticText[@value='Most Nights']"
                }
            },
            'smoke_frequency': {
                'question': "//XCUIElementTypeStaticText[@value='How often do you smoke?']",
                'options': {
                    'Social smoker': "//XCUIElementTypeStaticText[@value='Social smoker']",
                    'Smoker when drinking': "//XCUIElementTypeStaticText[@value='Smoker when drinking']",
                    'Non-smoker': "//XCUIElementTypeStaticText[@value='Non-smoker']",
                    'Smoker': "//XCUIElementTypeStaticText[@value='Smoker']",
                    'Trying to quit': "//XCUIElementTypeStaticText[@value='Trying to quit']"
                }
            },
            'workout_frequency': {
                'question': "//XCUIElementTypeStaticText[@value='Do you workout?']",
                'options': {
                    'Everyday': "//XCUIElementTypeStaticText[@value='Everyday']",
                    'Often': "//XCUIElementTypeStaticText[@value='Often']",
                    'Sometimes': "//XCUIElementTypeStaticText[@value='Sometimes']",
                    'Never': "//XCUIElementTypeStaticText[@value='Never']"
                }
            },
            'pets': {
                'question': "//XCUIElementTypeStaticText[@value='Do you have any pets?']",
                'options': {
                    'Dog': "//XCUIElementTypeStaticText[@value='Dog']",
                    'Cat': "//XCUIElementTypeStaticText[@value='Cat']",
                    'Reptile': "//XCUIElementTypeStaticText[@value='Reptile']",
                    'Amphibian': "//XCUIElementTypeStaticText[@value='Amphibian']",
                    'Bird': "//XCUIElementTypeStaticText[@value='Bird']",
                    'Fish': "//XCUIElementTypeStaticText[@value='Fish']",
                    "Don't have but love": "//XCUIElementTypeStaticText[@value=\"Don't have but love\"]",
                    'Other': "//XCUIElementTypeStaticText[@value='Other']",
                    'Turtle': "//XCUIElementTypeStaticText[@value='Turtle']",
                    'Hamster': "//XCUIElementTypeStaticText[@value='Hamster']",
                    'Rabbit': "//XCUIElementTypeStaticText[@value='Rabbit']",
                    'Pet-free': "//XCUIElementTypeStaticText[@value='Pet-free']",
                    'All the pets': "//XCUIElementTypeStaticText[@value='All the pets']",
                    'Want a pet': "//XCUIElementTypeStaticText[@value='Want a pet']",
                    'Allergic to pets': "//XCUIElementTypeStaticText[@value='Allergic to pets']"
                }
            }
        }
    },
    'what_makes_you_you': {
        'questions': {
            'communication_style': {
                'question': "//XCUIElementTypeStaticText[@value='What is your communication style?']",
                'options': {
                    'Big time texter': "//XCUIElementTypeStaticText[@value='Big time texter']",
                    'Phone caller': "//XCUIElementTypeStaticText[@value='Phone caller']",
                    'Video chatter': "//XCUIElementTypeStaticText[@value='Video chatter']",
                    'Bad texter': "//XCUIElementTypeStaticText[@value='Bad texter']",
                    'Better in person': "//XCUIElementTypeStaticText[@value='Better in person']"
                }
            },
            'how_do_you_receive_love': {
                'question': "//XCUIElementTypeStaticText[@value='How do you receive love?']",
                'options': {
                    'Thoughtful gestures': "//XCUIElementTypeStaticText[@value='Thoughtful gestures']",
                    'Presents': "//XCUIElementTypeStaticText[@value='Presents']",
                    'Touch': "//XCUIElementTypeStaticText[@value='Touch']",
                    'Compliments': "//XCUIElementTypeStaticText[@value='Compliments']",
                    'Time together': "//XCUIElementTypeStaticText[@value='Time together']"
                }
            },
            'education_level': {
                'question': "//XCUIElementTypeStaticText[@value='What is your education level?']",
                'options': {
                    'Bachelors': "//XCUIElementTypeStaticText[@value='Bachelors']",
                    'In College': "//XCUIElementTypeStaticText[@value='In College']",
                    'High School': "//XCUIElementTypeStaticText[@value='High School']",
                    'PhD': "//XCUIElementTypeStaticText[@value='PhD']",
                    'In Grad School': "//XCUIElementTypeStaticText[@value='In Grad School']",
                    'Masters': "//XCUIElementTypeStaticText[@value='Masters']",
                    'Trade School': "//XCUIElementTypeStaticText[@value='Trade School']"
                }
            },
            'zodiac_sign': {
                'question': "//XCUIElementTypeStaticText[@value='What is your zodiac sign?']",
                'options': {
                    'Capricorn': "//XCUIElementTypeStaticText[@value='Capricorn']",
                    'Aquarius': "//XCUIElementTypeStaticText[@value='Aquarius']",
                    'Pisces': "//XCUIElementTypeStaticText[@value='Pisces']",
                    'Aries': "//XCUIElementTypeStaticText[@value='Aries']",
                    'Taurus': "//XCUIElementTypeStaticText[@value='Taurus']",
                    'Gemini': "//XCUIElementTypeStaticText[@value='Gemini']",
                    'Cancer': "//XCUIElementTypeStaticText[@value='Cancer']",
                    'Leo': "//XCUIElementTypeStaticText[@value='Leo']",
                    'Virgo': "//XCUIElementTypeStaticText[@value='Virgo']",
                    'Libra': "//XCUIElementTypeStaticText[@value='Libra']",
                    'Scorpio': "//XCUIElementTypeStaticText[@value='Scorpio']",
                    'Sagittarius': "//XCUIElementTypeStaticText[@value='Sagittarius']"
                }
            }
        }
    },
    'hobbies': {
        'questions': {
            'interests': {
                'question': "//XCUIElementTypeStaticText[@value='What are you into?']",
                'options': {
                    'Harry Potter': "//XCUIElementTypeStaticText[@value='Harry Potter']",
                    '90s Kid': "//XCUIElementTypeStaticText[@value='90s Kid']",
                    'SoundCloud': "//XCUIElementTypeStaticText[@value='SoundCloud']",
                    'Spa': "//XCUIElementTypeStaticText[@value='Spa']",
                    'Self Care': "//XCUIElementTypeStaticText[@value='Self Care']",
                    'Heavy Metal': "//XCUIElementTypeStaticText[@value='Heavy Metal']",
                    'House Parties': "//XCUIElementTypeStaticText[@value='House Parties']",
                    'Gin tonic': "//XCUIElementTypeStaticText[@value='Gin tonic']",
                    'Gymnastics': "//XCUIElementTypeStaticText[@value='Gymnastics']",
                    'Hot Yoga': "//XCUIElementTypeStaticText[@value='Hot Yoga']",
                    'Meditation': "//XCUIElementTypeStaticText[@value='Meditation']",
                    'Spotify': "//XCUIElementTypeStaticText[@value='Spotify']",
                    'Sushi': "//XCUIElementTypeStaticText[@value='Sushi']",
                    'Hockey': "//XCUIElementTypeStaticText[@value='Hockey']",
                    'Basketball': "//XCUIElementTypeStaticText[@value='Basketball']",
                    'Slam Poetry': "//XCUIElementTypeStaticText[@value='Slam Poetry']",
                    'Home Workout': "//XCUIElementTypeStaticText[@value='Home Workout']",
                    'Theater': "//XCUIElementTypeStaticText[@value='Theater']",
                    'Cafe hopping': "//XCUIElementTypeStaticText[@value='Cafe hopping']",
                    'Aquarium': "//XCUIElementTypeStaticText[@value='Aquarium']",
                    'Sneakers': "//XCUIElementTypeStaticText[@value='Sneakers']",
                    'Instagram': "//XCUIElementTypeStaticText[@value='Instagram']",
                    'Hot Springs': "//XCUIElementTypeStaticText[@value='Hot Springs']",
                    'Walking': "//XCUIElementTypeStaticText[@value='Walking']",
                    'Running': "//XCUIElementTypeStaticText[@value='Running']",
                    'Travel': "//XCUIElementTypeStaticText[@value='Travel']",
                    'Language Exchange': "//XCUIElementTypeStaticText[@value='Language Exchange']",
                    'Movies': "//XCUIElementTypeStaticText[@value='Movies']",
                    'Guitarists': "//XCUIElementTypeStaticText[@value='Guitarists']",
                    'Social Development': "//XCUIElementTypeStaticText[@value='Social Development']",
                    'Gym': "//XCUIElementTypeStaticText[@value='Gym']",
                    'Social Media': "//XCUIElementTypeStaticText[@value='Social Media']",
                    'Hip Hop': "//XCUIElementTypeStaticText[@value='Hip Hop']",
                    'Skincare': "//XCUIElementTypeStaticText[@value='Skincare']",
                    'K-Pop': "//XCUIElementTypeStaticText[@value='K-Pop']",
                    'Potterhead': "//XCUIElementTypeStaticText[@value='Potterhead']",
                    'Trying New Things': "//XCUIElementTypeStaticText[@value='Trying New Things']",
                    'Photography': "//XCUIElementTypeStaticText[@value='Photography']",
                    'Bollywood': "//XCUIElementTypeStaticText[@value='Bollywood']",
                    'Reading': "//XCUIElementTypeStaticText[@value='Reading']",
                    'Singing': "//XCUIElementTypeStaticText[@value='Singing']",
                    'Sports': "//XCUIElementTypeStaticText[@value='Sports']",
                    'Poetry': "//XCUIElementTypeStaticText[@value='Poetry']"
                }
            }
        }
    }
}
