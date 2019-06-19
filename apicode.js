const exp=require('express')
const app=exp()
const bodyparser=require('body-parser')
const fs =require('fs')
const path= require('path')
const dir = path.join(__dirname,'form')
const multer = require('multer')
var upload=multer({dest:'upload/'})
app.use(bodyparser.urlencoded({extended:false}))

app.get('/',(req,res)=>{
    res.sendFile(path.join(dir,'homepage.html'))
})


app.post('/output',upload.fields([{
    name: 'leftfile',maxCount: 1
},{
    name: 'rightfile', maxCount:1
}
]),(req,res)=>{
    if(req.files){
        // console.log("code is here 1")
        const spawn=require('child_process').spawn
        const pythonProcess=spawn('python3',['./code.py',req.files.leftfile[0].filename,req.files.rightfile[0].filename])
        // console.log("code is here 2")
        pythonProcess.stdout.on('data',(data)=>{
            res.sendFile(path.join(__dirname + '/stiched_image.jpg'));
        })
    }
})

// app.post('/output',upload.fields([{
//     name: 'leftfile',maxCount: 1
// },{
//     name: 'rightfile', maxCount:1
// }
// ]),(req,res)=>{
//     console.log(req.files.leftfile[0].filename);
// })

app.listen(3000)