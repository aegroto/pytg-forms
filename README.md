# pytg-forms
"forms" module for PyTG

# Examples

## Info block

```
info: {
  first_step: STEP_ID
}
```

# Checkbox list
```
checkbox_cl: {
  type: checkbox_list,
  phrase: PHRASE_ID,
  entries: [
    [{text: "Option 1", data: "one"}], 
    [{text: "Option 2", data: "two"}], 
  ],
  confirm_step: STEP_ID,
  output: OUTPUT_VAR_NAME
}
```

# Text field 
```
textfield_tf: {
  type: text_field,
  phrase: PHRASE_ID,
  next_step: STEP_ID,
  output: OUTPUT_VAR_NAME
}
```

# Fixed reply
```
fixedreply_fr: {
  type: fixed_reply,
  phrase: PHRASE_ID,
  options: [
    [
      {text: "Image field", action: "jump;imagefield_if", output_data: "image"},
      {text: "Video field", action: "jump;videofield_vf", output_data: "video"},
      {text: "Animation field", action: "jump;animationfield_af",  output_data: "gif"},
    ],[
      {text: "Finish", action: "jump;None", output_data: "none"}
    ]
  ],
  next_step: STEP_ID,
  output: OUTPUT_VAR_NAME
}
```

# Image field 
```
image_if: {
  type: image_field,
  phrase: PHRASE_ID,
  next_step: STEP_ID,
  output: OUTPUT_VAR_NAME,
  save_in_cache: false
}
```

# Video field 
```
video_vf: {
  type: video_field,
  phrase: PHRASE_ID,
  next_step: STEP_ID,
  output: OUTPUT_VAR_NAME,
  save_in_cache: false
}
```

# Animation field 
```
animation_af: {
  type: animation_field,
  phrase: PHRASE_ID,
  next_step: STEP_ID,
  output: OUTPUT_VAR_NAME,
  save_in_cache: false
}
```
