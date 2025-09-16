# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AppointmentAppointment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    state = models.SmallIntegerField()
    date = models.DateTimeField()
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    report = models.TextField(blank=True, null=True)
    b2b_lead = models.ForeignKey('LeadsB2Blead', models.DO_NOTHING, blank=True, null=True)
    b2c_lead = models.ForeignKey('LeadsB2Clead', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appointment_appointment'


class AppointmentAppointmentUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    appointment = models.ForeignKey(AppointmentAppointment, models.DO_NOTHING)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'appointment_appointment_users'
        unique_together = (('appointment', 'user'),)




class BillingInvoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    bill_number = models.CharField(unique=True, max_length=50)
    due_date = models.DateField(blank=True, null=True)
    creation_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    state = models.SmallIntegerField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    lead = models.ForeignKey('LeadsB2Blead', models.DO_NOTHING, blank=True, null=True)
    updated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='billinginvoice_updated_by_set', blank=True, null=True)
    bill_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bill_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_invoice'


class BillingInvoiceitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.IntegerField()
    bill = models.ForeignKey(BillingInvoice, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'billing_invoiceitem'


class BillingQuote(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    bill_number = models.CharField(unique=True, max_length=50)
    due_date = models.DateField(blank=True, null=True)
    creation_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    state = models.SmallIntegerField()
    expiration_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    lead = models.ForeignKey('LeadsB2Blead', models.DO_NOTHING, blank=True, null=True)
    updated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='billingquote_updated_by_set', blank=True, null=True)
    bill_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bill_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_quote'


class BillingQuoteitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.IntegerField()
    bill = models.ForeignKey(BillingQuote, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'billing_quoteitem'


class BusinessBusinesssettings(models.Model):
    id = models.BigAutoField(primary_key=True)
    name_company = models.CharField(max_length=100)
    name_company_arabic = models.CharField(max_length=100, blank=True, null=True)
    logo = models.CharField(max_length=100, blank=True, null=True)
    logo_negatif = models.CharField(max_length=100, blank=True, null=True)
    favicon = models.CharField(max_length=100, blank=True, null=True)
    business_owner = models.CharField(max_length=50)
    business_owner_arabic = models.CharField(max_length=50, blank=True, null=True)
    wilaya = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    email2 = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    phone2 = models.CharField(max_length=50, blank=True, null=True)
    phone3 = models.CharField(max_length=50, blank=True, null=True)
    mini_about = models.CharField(max_length=80, blank=True, null=True)
    about = models.CharField(max_length=80, blank=True, null=True)
    rc_code = models.CharField(max_length=150, blank=True, null=True)
    art_code = models.CharField(max_length=150, blank=True, null=True)
    nif_code = models.CharField(max_length=150, blank=True, null=True)
    nis_code = models.CharField(max_length=150, blank=True, null=True)
    bank_number = models.CharField(max_length=50, blank=True, null=True)
    bank_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'business_businesssettings'


class BusinessBusinesssocials(models.Model):
    id = models.BigAutoField(primary_key=True)
    social_type = models.SmallIntegerField()
    link = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField()
    is_active = models.BooleanField()
    is_primary = models.BooleanField()
    business = models.ForeignKey(BusinessBusinesssettings, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'business_businesssocials'


class CoreLeadsource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'core_leadsource'


class CorePotential(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    segment = models.CharField(unique=True, max_length=1)
    min_employees = models.IntegerField()
    max_employees = models.IntegerField(blank=True, null=True)
    potentiel = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'core_potential'


class CoreTax(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    tax = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'core_tax'


class CrmActivitysector(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crm_activitysector'


class CrmCompany(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=100)
    business_owner = models.CharField(max_length=100, blank=True, null=True)
    employees_count = models.IntegerField()
    annual_tax = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    annual_goal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    facebook = models.CharField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=200, blank=True, null=True)
    linkedin = models.CharField(max_length=200, blank=True, null=True)
    instagram = models.CharField(max_length=200, blank=True, null=True)
    youtube = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    nif = models.CharField(max_length=20, blank=True, null=True)
    nrc = models.CharField(max_length=20, blank=True, null=True)
    nart = models.CharField(max_length=20, blank=True, null=True)
    nis = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    commune = models.ForeignKey('WilayasCommune', models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    potentiel = models.ForeignKey(CorePotential, models.DO_NOTHING, blank=True, null=True)
    wilaya = models.ForeignKey('WilayasWilaya', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crm_company'


class CrmCompanyActivitySectors(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)
    activitysector = models.ForeignKey(CrmActivitysector, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_company_activity_sectors'
        unique_together = (('company', 'activitysector'),)


class CrmCompanyTags(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)
    tags = models.ForeignKey('TagsTags', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_company_tags'
        unique_together = (('company', 'tags'),)


class CrmCompanydocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    document = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_companydocument'


class CrmCompanyemail(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    email = models.CharField(max_length=254)
    is_primary = models.BooleanField()
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_companyemail'


class CrmCompanyphone(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField()
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_companyphone'


class CrmContact(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    carte = models.CharField(unique=True, max_length=100, blank=True, null=True)
    hex_card = models.CharField(unique=True, max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    civility = models.CharField(max_length=3, blank=True, null=True)
    picture = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    blood = models.CharField(max_length=3)
    notes = models.TextField(blank=True, null=True)
    dette = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crm_contact'


class CrmContactSource(models.Model):
    id = models.BigAutoField(primary_key=True)
    contact = models.ForeignKey(CrmContact, models.DO_NOTHING)
    leadsource = models.ForeignKey(CoreLeadsource, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_contact_source'
        unique_together = (('contact', 'leadsource'),)


class CrmContactemail(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    email = models.CharField(max_length=254)
    is_primary = models.BooleanField()
    contact = models.ForeignKey(CrmContact, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_contactemail'


class CrmContactphone(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField()
    contact = models.ForeignKey(CrmContact, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'crm_contactphone'




class LeadsB2Blead(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    current_state = models.SmallIntegerField(blank=True, null=True)
    company = models.ForeignKey(CrmCompany, models.DO_NOTHING)
    current_state_user = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leads_b2blead'


class LeadsB2Bleadstate(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    state = models.SmallIntegerField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    lead = models.ForeignKey(LeadsB2Blead, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'leads_b2bleadstate'


class LeadsB2Clead(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    current_state = models.SmallIntegerField(blank=True, null=True)
    contact = models.ForeignKey(CrmContact, models.DO_NOTHING)
    current_state_user = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leads_b2clead'


class LeadsB2Cleadstate(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    state = models.SmallIntegerField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    lead = models.ForeignKey(LeadsB2Clead, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'leads_b2cleadstate'


class NotificationNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    object_id = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField()
    message = models.TextField()
    state = models.SmallIntegerField()
    link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField()
    content_type = models.ForeignKey(DjangoContentType, models.DO_NOTHING, blank=True, null=True)
    recipient = models.ForeignKey('UsersUser', models.DO_NOTHING)
    sender = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='notificationnotification_sender_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification_notification'


class TagsTags(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'tags_tags'


class TransactionsInvoicepayment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    payment_method = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    invoice = models.ForeignKey(BillingInvoice, models.DO_NOTHING)
    updated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='transactionsinvoicepayment_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_invoicepayment'


class TransactionsLedgerentry(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.CharField(max_length=100)
    date = models.DateField()
    description = models.CharField(max_length=255)
    entry_type = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    account = models.CharField(max_length=100)
    client_payment = models.ForeignKey(TransactionsInvoicepayment, models.DO_NOTHING, blank=True, null=True)
    misc_transaction = models.ForeignKey('TransactionsMisctransaction', models.DO_NOTHING, blank=True, null=True)
    staff_payment = models.ForeignKey('TransactionsStaffpayment', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_ledgerentry'


class TransactionsMisctransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    payment_method = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=250, blank=True, null=True)
    transaction_type = models.CharField(max_length=20)
    contact = models.ForeignKey(CrmContact, models.DO_NOTHING, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    updated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='transactionsmisctransaction_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_misctransaction'


class TransactionsStaffpayment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    payment_method = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    staff_member = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='transactionsstaffpayment_staff_member_set', blank=True, null=True)
    updated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='transactionsstaffpayment_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions_staffpayment'


class UsersAbsence(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_absent = models.BooleanField()
    date = models.DateField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_absence'
        unique_together = (('user', 'date'),)


class UsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(unique=True, max_length=254)
    picture = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    is_commercial = models.BooleanField()
    language = models.CharField(max_length=2)
    supervisor = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_groups'
        unique_together = (('user', 'group'),)


class UsersUserTags(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    tags = models.ForeignKey(TagsTags, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_tags'
        unique_together = (('user', 'tags'),)




class WilayasCommune(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    ar_name = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField()
    wilaya = models.ForeignKey('WilayasWilaya', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wilayas_commune'


class WilayasWilaya(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    ar_name = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    code = models.CharField(max_length=5)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'wilayas_wilaya'
