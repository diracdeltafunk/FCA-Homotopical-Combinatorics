stdin = $ScriptInputString <> Import["!cat","String"]
Export[$ScriptCommandLine[[2]], Image[ToExpression[stdin]], "AllowRasterization" -> False]