# Ministry Scheduler Pro Inv Upload

## Description

Get the ministers in an Involvement inside of TouchPoint.
    - within that Invovlement add them to the appropriate Sub Group...

## Journal

### February 19, 2025

So chardet is detecting:

```python
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result

# Example usage
file_path = "G:\general_admin_data\TouchPoint\imports\MSP (Ministry Scheduler Pro)\2025\MSP Touchpoint Roster 2.18.25.csv"
encoding = detect_encoding(file_path)
print(f"Detected encoding: {encoding}")

# output
{'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}

# output on TestFile
{'encoding': 'ISO-8859-1', 'confidence': 0.73, 'language': ''}
```

Not getting to the root of the issue but!
So now I am thinking maybe just read as latin-1???

```python
pd.read_csv('ml-100k/u.item', sep='|', names=m_cols , encoding='latin-1')
```

on reading the input with the latin encoding things go smoothly...

time to use the ai code? No luck :(

```python
import io

# Writing UTF-8 encoded data to StringIO
string_data = "你好，世界！"
string_io = io.StringIO()

# Encode the string to bytes using UTF-8 before writing
string_io.write(string_data.encode('utf-8').decode('utf-8'))

# Reset the file pointer to the beginning
string_io.seek(0)

# Read the data and decode it from UTF-8
retrieved_data = string_io.read()

# The `retrieved_data` variable now contains the original Unicode string
print(retrieved_data)

string_io.close()
```

Not working as I thought. I think it is due to the browser / javascript helping me...

```python
import io
# Writing UTF-8 encoded data to StringIO
string_data = model.Data.file
# string_io = io.StringIO()
bytes_io = io.BytesIO()

# Encode the string to bytes using UTF-8 before writing
# string_io.write(string_data.encode('latin-1').decode('utf-8'))
bytes_io.write(string_data)

# Reset the file pointer to the beginning
bytes_io.seek(0)

# Read the data and decode it from UTF-8
string_io = io.StringIO(bytes_io.read().decode('latin-1'))

# The `retrieved_data` variable now contains the original Unicode string
print_pgph(string_io.read())

# reader = csv.DictReader(string_io)

# ministrs_loaded = set()

# for row in reader:
#     ministr_tp_id = process_minister(row)
#     if ministr_tp_id:
#         ministrs_loaded.add(ministr_tp_id)

# unload_ministers_not_in_file(ministrs_loaded)

bytes_io.close()
string_io.close()
```

https://github.com/mholt/PapaParse/issues/169
https://stackoverflow.com/questions/4221176/excel-to-csv-with-utf8-encoding


Okay now I am just falling back to fix_text for the win!

And just add Archangel and Antifrion as replacement codes...

Only thing left would potentially be: (as far as I know now these are not SubGroups)

- Lider
- Addresses
- First name
- Last name

### February 20, 2025

back to latin-1 in and utf-8 out

for now...

first attempt:

```python
Traceback (most recent call last):
    File "", line 177, in
        File "", line 53, in
            process_post File "", line 81, in
                process_minister EnvironmentError: System.Data.SqlClient.SqlException (0x80131904): The INSERT statement conflicted with the FOREIGN KEY constraint "ORGANIZATION_MEMBERS_PPL_FK". The conflict occurred in database "CMS_stannparish", table "dbo.People", column 'PeopleId'. The statement has been terminated. at System.Data.SqlClient.SqlConnection.OnError(SqlException exception, Boolean breakConnection, Action`1 wrapCloseInAction) at System.Data.SqlClient.TdsParser.ThrowExceptionAndWarning(TdsParserStateObject stateObj, Boolean callerHasConnectionLock, Boolean asyncClose) at System.Data.SqlClient.TdsParser.TryRun(RunBehavior runBehavior, SqlCommand cmdHandler, SqlDataReader dataStream, BulkCopySimpleResultSet bulkCopyHandler, TdsParserStateObject stateObj, Boolean& dataReady) at System.Data.SqlClient.SqlCommand.FinishExecuteReader(SqlDataReader ds, RunBehavior runBehavior, String resetOptionsString, Boolean isInternal, Boolean forDescribeParameterEncryption, Boolean shouldCacheForAlwaysEncrypted) at System.Data.SqlClient.SqlCommand.RunExecuteReaderTds(CommandBehavior cmdBehavior, RunBehavior runBehavior, Boolean returnStream, Boolean async, Int32 timeout, Task& task, Boolean asyncWrite, Boolean inRetry, SqlDataReader ds, Boolean describeParameterEncryptionRequest) at System.Data.SqlClient.SqlCommand.RunExecuteReader(CommandBehavior cmdBehavior, RunBehavior runBehavior, Boolean returnStream, String method, TaskCompletionSource`1 completion, Int32 timeout, Task& task, Boolean& usedCache, Boolean asyncWrite, Boolean inRetry) at System.Data.SqlClient.SqlCommand.InternalExecuteNonQuery(TaskCompletionSource`1 completion, String methodName, Boolean sendToPipe, Int32 timeout, Boolean& usedCache, Boolean asyncWrite, Boolean inRetry) at System.Data.SqlClient.SqlCommand.ExecuteNonQuery() at System.Data.Linq.SqlClient.SqlProvider.Execute(Expression query, QueryInfo queryInfo, IObjectReaderFactory factory, Object[] parentArgs, Object[] userArgs, ICompiledSubQuery[] subQueries, Object lastResult) at System.Data.Linq.SqlClient.SqlProvider.ExecuteAll(Expression query, QueryInfo[] queryInfos, IObjectReaderFactory factory, Object[] userArguments, ICompiledSubQuery[] subQueries) at System.Data.Linq.SqlClient.SqlProvider.System.Data.Linq.Provider.IProvider.Execute(Expression query) at System.Data.Linq.ChangeDirector.StandardChangeDirector.DynamicInsert(TrackedObject item) at System.Data.Linq.ChangeProcessor.SubmitChanges(ConflictMode failureMode) at System.Data.Linq.DataContext.SubmitChanges(ConflictMode failureMode) at CmsData.CMSDataContext.SubmitChanges(ConflictMode failureMode) in D:\a\1\s\bvcms\CmsData\DbUtil\DbUtil.Context.cs:line 113 at CmsData.OrganizationMember.InsertOrgMembers(CMSDataContext db, Int32 organizationId, Int32 peopleId, Int32 memberTypeId, DateTime enrollmentDate, Nullable`1 inactiveDate, Boolean pending, String name, Boolean skipTriggerProcessing, Boolean isSMS) in D:\a\1\s\bvcms\CmsData\Organization\OrganizationMember.cs:line 416 at CmsData.OrganizationMember.InsertOrgMembers(CMSDataContext db, Int32 organizationId, Int32 peopleId, Int32 memberTypeId, DateTime enrollmentDate, Nullable`1 inactiveDate, Boolean pending, Boolean skipTriggerProcessing, Boolean isSMS) in D:\a\1\s\bvcms\CmsData\Organization\OrganizationMember.cs:line 440 at CmsData.PythonModel.JoinOrg(Object orgid, Object person) in D:\a\1\s\bvcms\CmsData\API\PythonModel\PythonModel.Organizations.cs:line 194 at CallSite.Target(Closure , CallSite , CodeContext , Object , Object , Object ) at process_minister$3714(Closure , PythonFunction , Object ) at lambda_method(Closure , Object[] , StrongBox`1[] , InterpretedFrame ) at Microsoft.Scripting.Interpreter.Interpreter.Run(InterpretedFrame frame) at Microsoft.Scripting.Interpreter.LightLambda.Run1[T0,TRet](T0 arg0) at System.Dynamic.UpdateDelegates.UpdateAndExecute2[T0,T1,TRet](CallSite site, T0 arg0, T1 arg1) at Microsoft.Scripting.Interpreter.DynamicInstruction`3.Run(InterpretedFrame frame) at Microsoft.Scripting.Interpreter.Interpreter.Run(InterpretedFrame frame) at Microsoft.Scripting.Interpreter.LightLambda.Run2[T0,T1,TRet](T0 arg0, T1 arg1) at IronPython.Compiler.PythonScriptCode.RunWorker(CodeContext ctx) at CmsData.PythonModel.ExecutePython(String script, PythonModel model, Boolean fromFile) in D:\a\1\s\bvcms\CmsData\API\PythonModel\PythonModel.Internal.cs:line 184 ClientConnectionId:60e7e30c-9c1a-45bd-971c-760b4679099c Error Number:547,State:0,Class:16
```


I'll just chunk the file by 200?

No, removed inserted records from file and tried another time with not entered people looks like the issue is not size problem.

Yep 78853 no longer exists. OOF
