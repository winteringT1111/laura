document.addEventListener('DOMContentLoaded', () => {
    const numberOfSnowflakes = 150;
    const body = document.body;

    for (let i = 0; i < numberOfSnowflakes; i++) {
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';

        // Set the initial position and animation properties
        snowflake.style.left = `${Math.random() * 100}vw`; // Random horizontal position
        snowflake.style.animationDuration = `${Math.random() * 10 + 20}s`; // Duration of rise
        snowflake.style.animationDelay = `${Math.random() * 20}s`; // Delay for staggered effect
        snowflake.style.transform = `scale(${Math.random() * 0.5 + 0.5})`; // Random size
        snowflake.style.opacity = Math.random(); // Random opacity

        body.appendChild(snowflake);
    }

    // Fade-in effect for paragraphs
    const paragraphs = document.querySelectorAll('.intro p');
    const initialDelay = 1000; // Initial delay for the first paragraph
    paragraphs.forEach((p, index) => {
        setTimeout(() => {
            p.classList.add('show'); // Add show class to make it appear
        }, initialDelay + index * 850); // Delay for subsequent paragraphs
    });

    // Set initial visibility for the clickable image
    const clickableImage = document.getElementById('clickableImage');
    setTimeout(() => {
        clickableImage.style.opacity = 1; // Make image visible
        clickableImage.style.transition = 'opacity 1s ease'; // Add animation
    }, 6600); // Set delay

    // Image click event
    if (clickableImage) {
        clickableImage.addEventListener('click', () => {
            // Fade out all paragraphs
            paragraphs.forEach(p => {
                p.style.transition = 'opacity 1s ease';
                p.style.opacity = 0;
            });

            const fadeOutDuration = 600; // Fade out duration
            setTimeout(() => {
                clickableImage.style.transition = 'transform 1s ease';
                clickableImage.style.transform = 'translateY(-430px)'; // Move image up

                // Show new content
                const newContent = document.querySelector('.new-content');
                newContent.style.display = 'block';
                setTimeout(() => {
                    newContent.classList.add('show');
                }, 1000); // Show content after image moves
            }, fadeOutDuration);
        });
    }

    // Timeline button click event
    const timelineButton = document.getElementById('timelineBtn');
    if (timelineButton) {
        timelineButton.addEventListener('click', () => {
            const newContent = document.querySelector('.new-content');
            const timelineContent = document.querySelector('.timeline');

            // Fade out new content and show timeline
            newContent.style.transition = 'opacity 1s ease';
            newContent.style.opacity = 0;

            setTimeout(() => {
                clickableImage.style.transition = 'opacity 0.5s ease'; 
                clickableImage.style.opacity = 0;
                clickableImage.style.display = 'none';
                newContent.style.display = 'none';
                timelineContent.style.display = 'block'; // Ensure it's set to block
                timelineContent.style.opacity = 0; // Start as invisible
                timelineContent.style.transition = 'opacity 1s ease'; // Add transition

                setTimeout(() => {
                    timelineContent.style.opacity = 1; // Fade in the timeline
                }, 10); // Short delay to trigger the transition
            }, 1000); // Wait for fade-out of new content
        });
    }
    // Camp button click event
    const campButton = document.getElementById('campBtn');
    if (campButton) {
        campButton.addEventListener('click', () => { 
            const newContent = document.querySelector('.new-content');
            const campContent = document.querySelector('.camp');

            // Fade out new content and show camp
            newContent.style.transition = 'opacity 1s ease';
            newContent.style.opacity = 0;

            setTimeout(() => {
                clickableImage.style.transition = 'opacity 0.5s ease'; 
                clickableImage.style.opacity = 0;
                clickableImage.style.display = 'none';
                newContent.style.display = 'none';
                campContent.style.display = 'block'; // Show the camp content
                campContent.style.opacity = 0; // Start as invisible
                campContent.style.transition = 'opacity 1s ease'; // Add transition
                setTimeout(() => {
                    campContent.style.opacity = 1; // Fade in the camp content
                }, 10); // Short delay to trigger the transition
            }, 1000); // Wait for fade-out of new content
        });
    }

});

    // Add timeline button click event
    const timelineButton2 = document.getElementById('timelineBtn2');
    if (timelineButton2) {
    timelineButton2.addEventListener('click', () => { 
        const campContent = document.querySelector('.camp');
        const timelineContent = document.querySelector('.timeline');


        setTimeout(() => {
            campContent.style.display = 'none'; // Hide the camp content
            timelineContent.style.display = 'block'; // Show the timeline content
            timelineContent.style.opacity = 0; // Start as invisible
            timelineContent.style.transition = 'opacity 1s ease'; // Add transition


            setTimeout(() => {
                timelineContent.style.opacity = 1; // Fade in the timeline
            }, 10); // Short delay to trigger the transition
        }, 1000); // Wait for fade-out of camp content
    });

    // Add camp button click event
    const campButton2 = document.getElementById('campBtn2');
    if (campButton2) {
    campButton2.addEventListener('click', () => { 
        const campContent = document.querySelector('.camp');
        const timelineContent = document.querySelector('.timeline');


        setTimeout(() => {
            timelineContent.style.display = 'none'; // Hide the camp content
            campContent.style.display = 'block'; // Show the timeline content
            campContent.style.opacity = 0; // Start as invisible
            campContent.style.transition = 'opacity 1s ease'; // Add transition

            setTimeout(() => {
                campContent.style.opacity = 1; // Fade in the timeline
            }, 10); // Short delay to trigger the transition
        }, 1000); // Wait for fade-out of camp content
    });
}
}