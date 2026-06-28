param([Parameter(ValueFromRemainingArguments = $true)] [string[]]$Args)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptDir/agent_cli.py" @Args
