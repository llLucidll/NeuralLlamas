# **Brain Flow: Mind-Controlled Music Suggestor and Generator**

![pic1](https://github.com/user-attachments/assets/3f8fd5ba-7a16-4432-9606-070b6491bb2d)


** Our DevPost Link **
https://devpost.com/software/focusflow-1u9ndy

As a team that struggled with focus and stress, we discovered the power of music in improving our well-being. This shared experience inspired us to enhance the way music helps individuals, using brain data to personalize recommendations.

FocusFlow uses real-time EEG data from users to refine music recommendations, tailoring them to align with each user's brain activity and improving their focus and calmness.

We used the Muse S to collect EEG data, a website built with Vanilla JavaScript, HTML, and CSS, and MongoDB to store user data. The Spotify API provided music tracks, and we fine-tuned its recommendation algorithm using brain data.

The biggest challenge was addressing conflicting interpretations of EEG bands in scientific literature, which we resolved with a Double-Blind Oddball Visual Paradigm test. We also navigated ethical and legal concerns related to storing brain data and working with copyrighted music.

We are proud of our polished product, created in just 64 hours, and our cohesive teamwork. Our generative model for music, leveraging state-of-the-art architecture, is another major milestone.

We gained valuable insights into brain function, scientific literature, and practical applications of our knowledge. Collaborating in an open, creative environment taught us the joy of turning passions into impactful projects.

We plan to refine our system with better metrics, improve performance with more data, and collaborate with industry experts to advance FocusFlow's capabilities.

## Training for the Users

![462554488_1249143069741344_384725285181268506_n](https://github.com/user-attachments/assets/7121d5d9-520c-45af-b2c6-0b7661110dfe)

As you start the website, we will have no idea who you are, and what kind of musics you like. So we have connected with Spotify to recommend the top songs that you listen to + a few generic focus / relax music to understand your brain waves. As we learn more about you, we will store your eeg data and average it out with the song and store it in Mongo for music suggestions and recommendations


## Suggesting Spotify songs on what helps you focus or relax based on users choice

![462557814_884408043457345_8454530162400073174_n](https://github.com/user-attachments/assets/c4635071-e7c5-4f6d-ad3a-f8f06616af5e)

When you click on either focus mode or relax mode, based on the mode we will see what kind of music peaks your concentration/calmness and based on that we would be recommending you songs from the Spotify Api. It is a radio feature such that when you click next, new music is generated. To the right hand side, you can also see the focus graph to keep tabs of your performance. 

## GenAI: Generating Music based on the mode and your eeg waves with Reinforcement Learning feedback loop

![462577843_1288581838944316_1374247918101071924_n](https://github.com/user-attachments/assets/263f9908-2c7a-4c44-8dc0-74a6554ec0a6)

When you click generate from the focus tab or the relax tab, we will be using a pre-existing gen ai model from Meta as we feed in our eeg waves and the model detects what kind of music you want. And to keep it accurate, we also require RL feedback loop to understand your choices better and generate better songs, suited for you
