const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static('public'));
app.use(express.static('.'));

let userQA = [];
let chatHistory = [];
let mealSuggestions = [];
let lastMealType = '';
let isFirstMessage = true;

function encodeData(data) {
    return Buffer.from(JSON.stringify(data)).toString('base64');
}

app.post('/create_profile', (req, res) => {
    const userMessage = req.body.message;
    const lastQuestion = req.body.lastQuestion;

    if (isFirstMessage) {
        isFirstMessage = false;
        res.json({
            response: "Hi! I'm here to help you create a personalized diet plan. Let's start by creating your profile. What's your name?",
            profileComplete: false
        });
    } else {
        chatHistory.push({ role: "user", content: userMessage });
        chatHistory.push({ role: "assistant", content: lastQuestion });

    
        userQA.push({
            question: lastQuestion,
            answer: userMessage
        });

        const encodedUserQA = encodeData(userQA);
        const encodedChatHistory = encodeData(chatHistory);

        const pythonCommand = `python create_profile.py analyze_profile_completeness "${encodedUserQA}" "${encodedChatHistory}"`;

        exec(pythonCommand, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error: ${error.message}`);
                return res.status(500).json({response: 'Error creating profile'});
            }
            if (stderr) {
                console.error(`stderr: ${stderr}`);
                return res.status(500).json({response: 'Error creating profile'});
            }

            const result = stdout.trim();

            if (result === "COMPLETE") {
                fs.writeFileSync('user_qa.json', JSON.stringify(userQA, null, 2));
                fs.writeFileSync('chat_history.json', JSON.stringify(chatHistory, null, 2));
                res.json({
                    response: "Great! Your profile is complete. You can now ask for meal suggestions, like 'I want to make breakfast'.",
                    profileComplete: true
                });
            } else {
                chatHistory.push({ role: "assistant", content: result });
                res.json({
                    response: result,
                    profileComplete: false
                });
            }
        });
    }
});

app.post('/get_clarification', (req, res) => {
    const { question, clarificationPrompt } = req.body;

    const encodedChatHistory = encodeData(chatHistory);

    const pythonCommand = `python create_profile.py get_clarification "${question}" "${clarificationPrompt}" "${encodedChatHistory}"`;

    exec(pythonCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            return res.status(500).json({response: 'Error getting clarification'});
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({response: 'Error getting clarification'});
        }

        const clarification = stdout.trim();
        chatHistory.push({ role: "assistant", content: clarification });
        res.json({ response: clarification });
    });
});

app.post('/get_meal_suggestion', (req, res) => {
    const userMessage = req.body.message.toLowerCase();

    if (userMessage.includes('breakfast')) lastMealType = 'breakfast';
    else if (userMessage.includes('lunch')) lastMealType = 'lunch';
    else if (userMessage.includes('dinner')) lastMealType = 'dinner';
    else if (userMessage.includes('snack')) lastMealType = 'snack';
    else lastMealType = 'meal';

    const mealRequest = JSON.stringify({
        mealType: lastMealType,
        userMessage: userMessage
    });
    fs.writeFileSync('meal_request.txt', mealRequest);

    if (userQA.length === 0) {
        try {
            const qaData = fs.readFileSync('user_qa.json', 'utf8');
            userQA = JSON.parse(qaData);
        } catch (error) {
            console.error('Error reading user_qa.json:', error);
            return res.status(500).json({suggestion: 'Error accessing user profile'});
        }
    }

    fs.writeFileSync('user_qa.json', JSON.stringify(userQA, null, 2));

    const scriptPath = path.join(__dirname, 'generate_meal_suggestion.py');
    const pythonCommand = `python "${scriptPath}"`;

    exec(pythonCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            return res.status(500).json({suggestion: 'Error generating meal suggestion'});
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({suggestion: 'Error generating meal suggestion'});
        }

        try {
            const result = JSON.parse(stdout.trim());
            const filename = result.filename;
            const message = result.message;

            mealSuggestions.push({filename, message});

            res.json({
                suggestion: `I've created a personalized ${lastMealType} suggestion for you: <a href="/${filename}" target="_blank">View Meal Suggestion</a>.`,
                mealUrl: `/${filename}`,
                message: message
            });
        } catch (parseError) {
            console.error(`Error parsing Python script output: ${parseError.message}`);
            return res.status(500).json({suggestion: 'Error processing meal suggestion'});
        }
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});