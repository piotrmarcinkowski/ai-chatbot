/* global use, db */
// MongoDB Playground
// To disable this template go to Settings | MongoDB | Use Default Template For Playground.
// Make sure you are connected to enable completions and to be able to run a playground.
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.
// The result of the last command run in a playground is shown on the results panel.
// By default the first 20 documents will be returned with a cursor.
// Use 'console.log()' to print to the debug output.
// For more documentation on playgrounds please refer to
// https://www.mongodb.com/docs/mongodb-vscode/playgrounds/

// Select the database to use.
use('chat_checkpoints_db');

// Doesn't work
// OperationFailure: FieldPath field names may not start with '$'. Consider using $getField
// firstMessage: { $first: "${checkpoint}.$binary.base64" },


// Return thread_id list
// Add first message from each chat thread
// TODO: try using $convert to convert binary to string
// https://www.mongodb.com/docs/manual/reference/operator/aggregation/convert/
db.getCollection('chat_checkpoints').aggregate([
  {
    $group: {
      _id: '$thread_id',
      firstMessage: { $first: '$checkpoint' }
    }
  },
  {
    $project: {
      _id: 1,
      firstMessage: 1
    }
  },
]).toArray().map(doc => ({
  ...doc,
  firstMessage: doc.firstMessage 
}));

// // Print all checkpoints in the collection.
// db.getCollection('chat_checkpoints').find().toArray()

