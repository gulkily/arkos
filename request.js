const fs = require('node:fs');

const prompt = `Create a workshop titled "Skill Development Session." The event should start on December 10th at 8:30 AM and end at 5:00 PM on the same day. Set the due time for 5:00 PM. Make it a recurring event every month.`;

let data = "";

fs.readFile('/Users/velocity/Documents/Holder/Project/CodingStuff/20ARK/json.txt', 'utf8', (err, fileData) => {
  if (err) {
    console.error(err);
    return;
  }
  data = fileData;  // Set the data variable after reading the file
  Test(data); // Call the Test function after the file is read
});

async function Test(data) {
    let response = await fetch("http://127.0.0.1:8080/completion", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prompt,
            n_predict: 512,
            json_schema: data,
        })
    });

    console.log((await response.json()).content);
}

