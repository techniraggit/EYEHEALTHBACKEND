health_prompts = {
    "Physical Health": [
        "🏋️ Tips to stay consistent with a daily workout routine.",
        "🥗 How to design a balanced meal plan for weight management.",
        "💪 Exercises to strengthen core muscles for better posture.",
        "❤️ Best practices for improving cardiovascular health.",
        "🦴 How to prevent and manage chronic back pain.",
        "💧 The role of hydration in physical performance.",
        "🚶‍♂️ Benefits of walking 10,000 steps a day.",
        "🌅 Morning stretches to boost energy for the day.",
        "📉 How to monitor and reduce blood pressure naturally.",
        "🦴 Foods to incorporate for optimal bone health."
    ],
    "Mental Health": [
        "🧘‍♂️ How to reduce stress and improve mental clarity.",
        "✨ Daily affirmations for boosting self-esteem.",
        "🕯️ Simple techniques for practicing mindfulness.",
        "🤝 How to manage anxiety in social situations.",
        "🙏 The impact of gratitude journaling on mental well-being.",
        "💬 Benefits of therapy and counseling for personal growth.",
        "🛁 How to create a self-care routine.",
        "⚡ Recognizing early signs of burnout and how to recover.",
        "😴 Tips to improve sleep quality for better mental health.",
        "🏃‍♀️ How physical activity contributes to mental well-being."
    ],
    "Nutrition": [
        "🌟 Superfoods to include in your diet and their benefits.",
        "🍳 The importance of macronutrients and how to balance them.",
        "🍭 How to reduce sugar intake without sacrificing taste.",
        "🥦 Plant-based sources of protein for vegetarians.",
        "🍎 Healthy snacks for people on the go.",
        "🦠 The role of probiotics in gut health.",
        "💧 How to make water more interesting to drink.",
        "🛡️ Foods to boost your immune system.",
        "🥡 Meal prepping ideas for a week of healthy eating.",
        "⏳ The benefits of intermittent fasting."
    ],
    "Sleep and Recovery": [
        "🛌 How to set up the ideal bedroom for better sleep.",
        "🌬️ Breathing exercises to fall asleep faster.",
        "🧠 The importance of REM sleep for cognitive function.",
        "😴 How naps can improve your productivity and health.",
        "📱 The effects of blue light on sleep and how to mitigate it.",
        "⏰ How to establish a bedtime routine for consistent sleep.",
        "🍷 Foods and drinks to avoid before bedtime.",
        "🧘‍♀️ The role of meditation in improving sleep quality.",
        "🛠️ Best sleeping positions for spinal health.",
        "💤 How to manage sleep disorders like insomnia."
    ],
    "Fitness": [
        "🏋️‍♀️ Best exercises for beginners to start a fitness journey.",
        "🤔 Cardio vs. strength training: which is better?",
        "🧘 Benefits of yoga for flexibility and stress relief.",
        "🩹 How to recover from muscle soreness after workouts.",
        "⚠️ Tips to avoid injuries while exercising.",
        "📊 How to track your fitness progress effectively.",
        "🦵 The importance of stretching before and after workouts.",
        "🏠 Home workout routines for busy individuals.",
        "🏊 The benefits of swimming for full-body fitness.",
        "🏃 How to train for a 5K or marathon."
    ],
    "Preventative Health": [
        "🛡️ How to build a strong immune system year-round.",
        "🏥 The importance of regular health check-ups.",
        "🔍 How to self-check for potential health issues.",
        "💉 Vaccinations and their role in preventing diseases.",
        "🪥 Best practices for maintaining oral hygiene.",
        "❤️‍🩹 Tips for managing cholesterol levels.",
        "☀️ The importance of sunscreen in preventing skin damage.",
        "🧼 How to develop a habit of washing hands effectively.",
        "🌼 How to manage and prevent seasonal allergies.",
        "🍇 The role of antioxidants in disease prevention."
    ],
    "Holistic and Alternative Health": [
        "🌿 The benefits of acupuncture for pain management.",
        "🕯️ How aromatherapy can improve your mood.",
        "🍵 Benefits of herbal teas for relaxation and digestion.",
        "🧘‍♂️ The role of meditation in holistic health.",
        "🪷 Exploring the benefits of Ayurveda for lifestyle changes.",
        "🦵 How chiropractic adjustments can improve mobility.",
        "🤲 Benefits of massage therapy for stress relief.",
        "🌡️ Natural remedies for common cold symptoms.",
        "🌸 The role of essential oils in boosting energy.",
        "🌍 How to practice grounding techniques for overall wellness."
    ],
    "Health and Technology": [
        "📱 Best health apps to track fitness and nutrition.",
        "⌚ How wearable devices can improve health monitoring.",
        "💻 The impact of screen time on physical and mental health.",
        "🩺 How telemedicine is changing healthcare access.",
        "📲 Using apps to track and improve mental health.",
        "🪑 How to stay active in a tech-driven sedentary lifestyle.",
        "🎮 The role of virtual reality in physical therapy.",
        "📈 Fitness trackers: are they worth it?",
        "💪 Best online workout programs for home fitness.",
        "🛌 How to use technology to improve sleep quality."
    ],
    "Lifestyle and Healthy Habits": [
        "🍃 How to transition to a healthier lifestyle gradually.",
        "🚭 Tips to quit smoking and maintain a smoke-free life.",
        "🚶 Simple habits to stay active throughout the day.",
        "⏳ How to manage time effectively for a balanced lifestyle.",
        "💡 How to avoid burnout while maintaining productivity.",
        "⚖️ Steps to cultivate a healthy work-life balance.",
        "👥 The impact of social connections on overall health.",
        "✈️ How to stay healthy while traveling.",
        "🕒 Managing health goals with a busy schedule.",
        "🚫 How to identify and eliminate unhealthy habits."
    ],
    "Specialized Health Topics": [
        "🤰 Exercises and nutrition for pregnant women.",
        "🩸 Managing diabetes through lifestyle changes.",
        "👵 The impact of aging on physical health and how to adapt.",
        "🦵 How to manage arthritis with exercise and diet.",
        "⚕️ Tips for maintaining a healthy weight post-surgery.",
        "🧠 The importance of mental health in chronic illness.",
        "👶 Nutrition and exercise for children and teenagers.",
        "🏃‍♀️ How to maintain healthy joints as you age.",
        "📉 How to cope with health issues affecting daily life.",
        "🤝 Tips to support loved ones dealing with illness."
    ]
}


from project_setup import *

from ai_doctor.models.models import Category, PredefinedPrompts

Category.objects.all().delete()
PredefinedPrompts.objects.all().delete()
for category, prompts in health_prompts.items():
    c = Category.objects.get_or_create(name=category)[0]
    for prompt in prompts:
        PredefinedPrompts.objects.get_or_create(category=c, prompt=prompt)
