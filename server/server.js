#!/usr/bin/node

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
      res.render('index',{output: err, data:req.body.data});
      return
    }
    console.log("The file was saved!");
  });

  let options = {
    mode: 'text',
    pythonPath: 'python3',
    encoding: 'utf8',
    pythonOptions: ['-u'], // get print results in real-time
    scriptPath: './',
    args: ['input.txt', './public/img/graph']
  };

  PythonShell.run('../reduction.py', options, function (err, results) {
    if (err)  {
      console.log('error minisat');
      res.render('index',{output: err, data:req.body.data});
      return;
    }
    console.log('got minisat', results);
    // exec('./minisat_release ./output.txt ./output2.txt', (err) => {
    //   if(err) {
    //     return console.log(err);
    //   }
    if(results == "UNSAT") {
        res.render('index',{output: results, data: req.body.data});
        return
    }
    res.render('index',{output: "", data: req.body.data});
    // });
  });
});

app.listen(process.env.PORT || 5002, function () {
  console.log('App listening on port 5002!')
});
