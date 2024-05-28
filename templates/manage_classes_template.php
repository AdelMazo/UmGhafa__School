<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Classes</title>
</head>
<body>
    <h1>Manage Classes</h1>
    <table border="1">
        <thead>
            <tr>
                <th>#</th>
                <th>Class Name</th>
                <th>Class Name Numeric</th>
                <th>Section</th>
                <th>Creation Date</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($classes_data as $row): ?>
                <tr>
                    <td><?php echo $row['id']; ?></td>
                    <td><?php echo $row['ClassName']; ?></td>
                    <td><?php echo $row['ClassNameNumeric']; ?></td>
                    <td><?php echo $row['Section']; ?></td>
                    <td><?php echo $row['CreationDate']; ?></td>
                    <td><a href="#" onclick="showUpdateForm(<?php echo $row['id']; ?>)">Edit</a></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>

    <!-- JavaScript -->
    <script>
        function showUpdateForm(id) {
            alert('Update form for class ID ' + id);
            // Add your code to show the update form
        }
    </script>
</body>
</html>
