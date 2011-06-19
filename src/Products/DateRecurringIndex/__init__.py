def initialize(context):
    import index
    context.registerClass(
            index.DateRecurringIndex,
            permission='Add Pluggable Index',
            constructors=(index.manage_addDRIndexForm,
                          index.manage_addDRIndex),
            icon='www/index.gif',
            visibility=None
    )
