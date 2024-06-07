SMS_TEMPLATE = {
    "send_otp": "Hi! Your EyeMyEye verification code is {otp}. It is valid for 15 mins. s80mPWzCpOC"
}

ERROR_500_MSG = "An unexpected server error occurred. Please contact support."

EVENT_CHOICES = (
    ("eye_test", "Eye Test"),
    ("fatigue_test", "Fatigue Test"),
    ("prescription_upload", "Prescription Upload"),
    ("referral", "Referral"),
)

FATIGUE_SUGGESTIONS_AND_HEALTH_SCORES = [
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": False,
        "health_score": 10,
        "suggestion": "You surprised us. Your eye health score is 10/10 \n We recommended you to keep testing your eyes every 4 hours  \n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": False,
        "health_score": 7,
        "suggestion": "Your eye health score is 7. Your right eye is fatigued due to excess strain. \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply cold towel over the eyes if possible\n Reduce digital screen time or bright light exposure for sometime\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": False,
        "health_score": 7,
        "suggestion": "Your eye health score is 7. Your eyes are tired. There is dryness in the eye and possibility of itching if this condition prolongs. \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible.\n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light. You should aim for a good sleep of over 7 hours.\n If dryness persists over a prolonged period please consult your eye doctor\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 7,
        "suggestion": "Your eye health score is 7. Your right eye is fatigued due to excess strain. \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply cold towel over the eyes if possible\n Reduce digital screen time or bright light exposure for sometime\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": True,
        "health_score": 7,
        "suggestion": "Your eye health score is 7. Your eyes are tired. There is dryness in the eye and possibility of itching if this condition prolongs.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light. You should aim for a good sleep of over 7 hours.\n If dryness persists over a prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": False,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are fatigued. There is dryness in the eye and possibility of itching if this condition prolongs. You might feel burning sensation in your eyes.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices  and avoid exposure to bright light.\n If burning sensation persists for over a day, visit your eye doctor for medication\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": True,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": True,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 5,
        "suggestion": "Your eye health score is 5. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 3,
        "suggestion": "Your eye health score is 3. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs. You might feel burning sensation in your eyes.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices  and avoid exposure to bright light.\n If burning sensation persists for over a day, visit your eye doctor for medication\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": False,
        "is_mild_tiredness_left": True,
        "health_score": 3,
        "suggestion": "Your eye health score is 3. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs.  \n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n If driving, stop and relax for a couple of minutes. Refrain from looking at digital devices  and avoid exposure to bright light.\n If dryness persists over prolonged period please consult your eye doctor  \n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 3,
        "suggestion": "Your eye health score is 3. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs. You might feel burning sensation in your eyes.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices  and avoid exposure to bright light.\n If burning sensation persists for over a day, visit your eye doctor for medication\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 3,
        "suggestion": "Your eye health score is 3. Your eyes are fatigued and tired. There is dryness in the eye and possibility of itching if this condition prolongs. You might feel burning sensation in your eyes.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices  and avoid exposure to bright light.\n If burning sensation persists for over a day, visit your eye doctor for medication\n Come back and check again every 4 hours to track the progress of improvement\n Follow the practice of looking at an object 20 feet away for 20 seconds every 20 minutes.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": False,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": False,
        "is_mild_tiredness_right": False,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 2,
        "suggestion": "Your eye health score is 2. Your eyes are extremely tired and fatigued.\n Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. \n Refrain from looking at digital devices and avoid exposure to bright light. Your eyes need rest and sleep for at least 7-8 hours a day. \n Come back and check again every 4 hours to track the progress of improvement\n If your eyes still feel tired after a sleep, please visit your eye doctor.",
    },
    {
        "is_fatigue_right": True,
        "is_mild_tiredness_right": True,
        "is_fatigue_left": True,
        "is_mild_tiredness_left": True,
        "health_score": 0,
        "suggestion": "Your eye health score is 0. Your eyes are extremely tired and fatigued. You should not take this lightly. Immediately relieve your eyes of strain by closing them for 5 minutes, apply a cold towel over the eyes if possible. Refrain from looking at digital devices and avoid exposure to bright light.\n You might need eye drops for medication. Consult your eye doctor without delay and follow the medication prescribed. \n Avoid exposure to digital devices for over a day or more as prescribed by your doctor.",
    },
]
