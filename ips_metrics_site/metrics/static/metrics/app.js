var TableSorter = {
    makeSortable: function(table){
        // Store context of this in the object
        var _this = this;
        var th = table.tHead, i;
        th && (th = th.rows[0]) && (th = th.cells);  // Looks like progressively narrowing th's definition + 3 checks for success?
        // Probably need to research the .tHead, and .rows, and .cells
        if (th){
            i = th.length;
        }else{
            return; // if no `<thead>` then do nothing
        }

        // Loop through every <th> inside the header
        while (--i >= 0) (function (i) {
            var dir = 1;

            // Append click listener to sort
            th[i].addEventListener('click', function () {
                _this._sort(table, i, (dir = 1 - dir));
            });
        }(i));
    },
    _sort: function (table, col, reverse) {
        var tb = table.tBodies[0], // use `<tbody>` to ignore `<thead>` and `<tfoot>` rows
        tr = Array.prototype.slice.call(tb.rows, 0), // put rows into array
        i;

        //reverse = -((+reverse) || -1);  // I guess this takes a boolean and transforms it - False = 1 and True = -1. The '+' is unnecessary though.
        if (reverse) { // Would much prefer to do this outside _sort and simply provide the correct modifier, or something. This is ugly.
            reverse = -1
        }
        else {
            reverse = 1
        }

        

        // Need to add an additional step that determines if this col is a column of integers:
        let isNumeric = true;
        for (i=0; i<tr.length; i++) {
            val = tr[i].cells[col].textContent;
            if (val!=parseInt(val,10)) {
                isNumeric = false;
                break;
            }
            // console.log(val + parseInt(val));
            // console.log("Row #" + i + " col#" + col + ": " + tr[i].cells[col].textContent + "  isInt:" + (val == parseInt(val, 10)));
            // console.log("Row #" + i + " col#" + col + ": " + tr[i].cells[col].textContent + "  isNaN:" + isNaN(parseInt(tr[i].cells[col].textContent)));
        }

        let isDate = false;
        if (!isNumeric) {
            //Checking the results of date parsing:
            isDate = true;
            for (i=0; i<tr.length; i++) {
                val = tr[i].cells[col].textContent;
                // console.log("Val: " + val + " parsed as date: " + Date.parse(val));
                if (Number.isNaN(Date.parse(val))) {
                    isDate = false;
                    break;
                }
            }
        }

        // console.log("Column isDate: " + isDate);

        // console.log("isNumeric: " + isNumeric)
        
        // function (tr, col) {
        //     console.log("Running... on col #" + col);
        //     // let result = false;
        //     // for (i=0; i<tr.length; i++) {
        //     //     console.log("Row #" + i + " parseInt:" + parseInt(tr[i].cells[col].textContent));
        //     // }
        //     return false;
        // }

        // console.log("" + isNumeric());
        


        // Sort rows
        

        tr = tr.sort(function (a, b) {
            // `-1 *` if want opposite order
            if (isNumeric) {
                return reverse * (parseInt(a.cells[col].textContent, 10)-parseInt(b.cells[col].textContent, 10));
            }
            else if (isDate) {
                return reverse * (Date.parse(a.cells[col].textContent, 10)-Date.parse(b.cells[col].textContent, 10));
            }
            else {
                return reverse * (
                    // Using `.textContent.trim()` for test
                    
                    a.cells[col].textContent.trim().localeCompare(
                        b.cells[col].textContent.trim()
                    )
                );
            }
            
            
        });

        for(i = 0; i < tr.length; ++i){
            // Append rows in new order
            tb.appendChild(tr[i]);
        }
    }
};