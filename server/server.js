const express = require('express');
const bodyParser = require('body-parser');
const {PythonShell} = require("python-shell");
const { exec } = require('child_process');
const fs = require('fs');
const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));

app.get('/', function (req, res) {
  res.render('index',{output: " ", data: ""});
});

app.post('/generate', function (req, res) {
  fs.writeFile("input.txt", req.body.data, function(err) {
    if(err) {
      return console.log(err);
    }
    console.log("The file was saved!");
  });

  let options = {
    mode: 'text',
    pythonPath: '/anaconda3/bin/python3',// '/usr/local/bin/python3','
    encoding: 'utf8',
    pythonOptions: ['-u'], // get print results in real-time
    scriptPath: './',
    args: ['input.txt']
  };

  PythonShell.run('dimacs.py', options, function (err) {
    if (err)  {
      res.render('index',{output: err, data:req.body.data});
      return;
    }
    exec('./minisat_release ./output.txt ./output2.txt', () => {
      res.render('index',{output: "", data: req.body.data});
    });
  });
});

app.listen(process.env.PORT || 5000, function () {
  console.log('App listening on port 5000!')
});
